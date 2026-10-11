import os, re, uuid, time, shutil, subprocess, threading
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from gtts import gTTS
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}, r"/videos/*": {"origins": "*"}})
ROOT = Path(__file__).resolve().parent
OUT = Path(os.environ.get("VIDEO_DIR", "/tmp/linkora-tutorial-videos"))
OUT.mkdir(parents=True, exist_ok=True)
MAX_CHARS = 12000
MAX_SCENES = 18
TTL_SECONDS = 12 * 60 * 60
LOCK = threading.Lock()

def cleanup():
    now = time.time()
    for p in OUT.iterdir():
        try:
            if now - p.stat().st_mtime > TTL_SECONDS:
                shutil.rmtree(p) if p.is_dir() else p.unlink()
        except OSError:
            pass

def split_scenes(transcript):
    blocks = [re.sub(r"\s+", " ", b).strip() for b in re.split(r"\n\s*\n", transcript) if b.strip()]
    scenes = []
    for block in blocks:
        # Split long paragraphs at sentence boundaries while keeping each narration segment manageable.
        sentences = re.split(r"(?<=[.!?।])\s+", block)
        current = ""
        for sentence in sentences:
            if current and len(current) + len(sentence) > 550:
                scenes.append(current.strip()); current = sentence
            else:
                current = (current + " " + sentence).strip()
        if current:
            scenes.append(current.strip())
    return scenes[:MAX_SCENES]

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    for f in candidates:
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()

def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if line and draw.textbbox((0, 0), trial, font=fnt)[2] > max_width:
            lines.append(line); line = word
        else:
            line = trial
    if line: lines.append(line)
    return lines

def make_slide(path, title, body, number, total):
    W, H = 1280, 720
    im = Image.new("RGB", (W, H), "#080d09")
    d = ImageDraw.Draw(im)
    d.ellipse((890, -190, 1450, 370), outline="#334a25", width=3)
    d.ellipse((970, -110, 1370, 290), outline="#26381e", width=2)
    d.rounded_rectangle((72, 62, 1208, 658), radius=28, fill="#121a13", outline="#31432b", width=2)
    d.rounded_rectangle((108, 98, 1172, 106), radius=4, fill="#c7ff4d")
    d.text((112, 138), f"LINKORA LEARN  •  LESSON {number:02d}/{total:02d}", font=font(23, True), fill="#c7ff4d")
    title_lines = wrap_text(d, title, font(44, True), 1030)
    y = 205
    for line in title_lines[:2]:
        d.text((112, y), line, font=font(44, True), fill="#f5f8f2")
        y += 62
    y += 20
    body_lines = wrap_text(d, body, font(30), 1010)
    for line in body_lines[:7]:
        d.text((116, y), line, font=font(30), fill="#cbd8c8")
        y += 48
    d.text((112, 600), "বাংলা টিউটোরিয়াল • Transcript-based video", font=font(19), fill="#91a48c")
    im.save(path)

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=240)
    if p.returncode:
        raise RuntimeError((p.stderr or "Media processing failed")[-1800:])

@app.get("/")
def health():
    return jsonify({"service":"Linkora Tutorial Video Studio","status":"ok","max_chars":MAX_CHARS,"max_scenes":MAX_SCENES,"video_retention_hours":12})

@app.post("/api/generate")
def generate():
    payload = request.get_json(silent=True) or {}
    transcript = str(payload.get("transcript", "")).strip()
    title = str(payload.get("title", "বাংলা টিউটোরিয়াল")).strip()[:100] or "বাংলা টিউটোরিয়াল"
    if len(transcript) < 40:
        return jsonify({"error":"কমপক্ষে ৪০ অক্ষরের transcript দিন।"}), 400
    if len(transcript) > MAX_CHARS:
        return jsonify({"error":f"Transcript সর্বোচ্চ {MAX_CHARS} অক্ষরের হতে পারবে।"}), 413
    scenes = split_scenes(transcript)
    if not scenes:
        return jsonify({"error":"Transcript থেকে scene তৈরি করা যায়নি।"}), 400
    job_id = uuid.uuid4().hex[:12]
    job = OUT / job_id
    job.mkdir(parents=True)
    try:
        parts = []
        for i, text in enumerate(scenes, 1):
            slide = job / f"slide_{i:02d}.png"
            audio = job / f"audio_{i:02d}.mp3"
            segment = job / f"segment_{i:02d}.mp4"
            make_slide(slide, title if i == 1 else f"ধাপ {i}: {text[:60]}", text, i, len(scenes))
            # gTTS provides Bengali narration over the network; it is not an offline voice.
            gTTS(text=text, lang="bn", slow=False).save(str(audio))
            run([FFMPEG,"-y","-loop","1","-i",str(slide),"-i",str(audio),"-c:v","libx264","-preset","ultrafast","-tune","stillimage","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(segment)])
            parts.append(segment)
        concat_file = job / "concat.txt"
        concat_file.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
        video = job / "tutorial.mp4"
        run([FFMPEG,"-y","-f","concat","-safe","0","-i",str(concat_file),"-c","copy","-movflags","+faststart",str(video)])
        (job / "meta.txt").write_text(title + "\n" + str(len(scenes)), encoding="utf-8")
        return jsonify({"ok":True,"id":job_id,"title":title,"scenes":len(scenes),"video_url":f"/videos/{job_id}/tutorial.mp4","download_url":f"/videos/{job_id}/tutorial.mp4","note":"ভিডিও ১২ ঘণ্টা পর্যন্ত এই সার্ভিসে রাখা হবে; স্থায়ী archive/storage আলাদা করে configure করতে হবে।"})
    except Exception as e:
        shutil.rmtree(job, ignore_errors=True)
        app.logger.exception("Video generation failed")
        return jsonify({"error":"ভিডিও তৈরি করা যায়নি। Server log দেখুন; transcript ছোট করে আবার চেষ্টা করুন।","detail":str(e)[:500]}), 500

@app.get("/videos/<job_id>/<filename>")
def serve_video(job_id, filename):
    cleanup()
    if not re.fullmatch(r"[a-f0-9]{12}", job_id) or filename != "tutorial.mp4":
        return jsonify({"error":"ভিডিও পাওয়া যায়নি বা মেয়াদ শেষ।"}), 404
    folder = OUT / job_id
    path = folder / filename
    if not path.is_file():
        return jsonify({"error":"ভিডিও পাওয়া যায়নি বা ১২ ঘণ্টার retention শেষ।"}), 404
    return send_from_directory(folder, filename, mimetype="video/mp4", as_attachment=False, max_age=0)

@app.get("/api/status/<job_id>")
def status(job_id):
    if not re.fullmatch(r"[a-f0-9]{12}", job_id):
        return jsonify({"error":"Invalid ID"}), 400
    p = OUT / job_id / "tutorial.mp4"
    if p.is_file():
        return jsonify({"ready":True,"size_bytes":p.stat().st_size})
    return jsonify({"ready":False}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
