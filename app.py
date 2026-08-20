from flask import Flask, render_template, request, jsonify
from pathlib import Path
import subprocess, tempfile, json, shutil, sys, re, os

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
ENGINE = BASE_DIR / "lead_bot.py"
ENGINE_TIMEOUT = int(os.environ.get("ENGINE_TIMEOUT", "75"))

def extract_summary(output):
    def find(pattern):
        m = re.search(pattern, output)
        return m.group(1) if m else None
    return {
        "qualified": find(r"Nitelikli lead:\s*(\d+)"),
        "route_count": find(r"Bugünkü rota:\s*(\d+) işletme"),
        "walk_km": find(r"Toplam yürüyüş:\s*([0-9.]+) km"),
        "walk_min": find(r"Tahmini saf yürüyüş:\s*~(\d+) dk"),
    }

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/health")
def health():
    return {"ok": True, "version": "Cihan Vision Mobile v2.3"}

@app.post("/api/route")
def create_route():
    data = request.get_json(silent=True) or {}
    try:
        lat, lon = float(data["lat"]), float(data["lon"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"ok": False, "error": "Konum bilgisi okunamadı."}), 400

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return jsonify({"ok": False, "error": "Geçersiz koordinat."}), 400

    with tempfile.TemporaryDirectory(prefix="cihanvision_") as tmp:
        tmp_path = Path(tmp)
        shutil.copy2(ENGINE, tmp_path / "lead_bot.py")
        try:
            proc = subprocess.run(
                [sys.executable, "-u", str(tmp_path / "lead_bot.py")],
                input=f"{lat},{lon}\n", text=True, capture_output=True,
                cwd=tmp_path, timeout=ENGINE_TIMEOUT,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
        except subprocess.TimeoutExpired as exc:
            partial = (exc.stdout or "")
            if isinstance(partial, bytes):
                partial = partial.decode(errors="ignore")
            app.logger.warning("ENGINE TIMEOUT: %s", partial[-2000:])
            return jsonify({
                "ok": False,
                "error": "Harita servisleri bu denemede yavaş kaldı. Tekrar dene.",
                "stage": "engine_timeout"
            }), 504

        output = (proc.stdout or "") + "\n" + (proc.stderr or "")
        app.logger.info("ENGINE rc=%s tail=%s", proc.returncode, output[-1800:])
        route_file = tmp_path / "bugunun_rotasi.json"

        if proc.returncode != 0 or not route_file.exists():
            message = "Rota oluşturulamadı."
            if "OSM VERİSİ EKSİK" in output:
                message = "OSM sunucuları şu an yoğun. Tekrar dene."
            elif "nitelikli lead yok" in output.lower():
                message = "Bu bölgede filtreyi geçen nitelikli lead bulunamadı."
            return jsonify({"ok": False, "error": message, "log_tail": output[-2500:]}), 502

        try:
            leads = json.loads(route_file.read_text(encoding="utf-8"))
        except Exception:
            return jsonify({"ok": False, "error": "Rota çıktısı okunamadı."}), 500

        return jsonify({
            "ok": True,
            "start": {"lat": lat, "lon": lon},
            "leads": leads,
            "summary": extract_summary(output),
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
