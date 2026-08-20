from flask import Flask, render_template, request, jsonify
from lead_engine import make_leads
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return {
        "ok": True,
        "version": "Cihan Vision v3.1"
    }


@app.post("/api/route")
def route():
    data = request.get_json(silent=True) or {}

    # --------------------------------------------------------
    # KONUM KONTROLÜ
    # --------------------------------------------------------

    try:
        lat = float(data["lat"])
        lon = float(data["lon"])
    except (KeyError, TypeError, ValueError):
        return jsonify({
            "ok": False,
            "error": "Konum bilgisi okunamadı."
        }), 400

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return jsonify({
            "ok": False,
            "error": "Geçersiz koordinat."
        }), 400

    app.logger.info(
        "Rota isteği alındı: lat=%s lon=%s",
        lat,
        lon
    )

    # --------------------------------------------------------
    # LEAD MOTORU
    # --------------------------------------------------------

    try:
        result = make_leads(lat, lon)

        if not isinstance(result, dict):
            raise ValueError(
                "Lead motoru beklenmeyen veri döndürdü."
            )

        leads = result.get("leads", [])
        summary = result.get("summary", {})

        app.logger.info(
            "Rota tamamlandı. Qualified=%s Route=%s",
            summary.get("qualified"),
            len(leads)
        )

        return jsonify({
            "ok": True,
            "start": {
                "lat": lat,
                "lon": lon
            },
            "leads": leads,
            "summary": summary
        })

    # --------------------------------------------------------
    # OSM / VERİ HATASI
    # --------------------------------------------------------

    except RuntimeError as e:
        app.logger.error(
            "LEAD ENGINE RuntimeError: %s",
            str(e)
        )

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 503

    # --------------------------------------------------------
    # BEKLENMEYEN HATA
    # --------------------------------------------------------

    except Exception as e:
        app.logger.exception(
            "ROUTE ERROR: %s",
            str(e)
        )

        return jsonify({
            "ok": False,
            "error": "Rota oluşturulurken beklenmeyen bir hata oluştu."
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
