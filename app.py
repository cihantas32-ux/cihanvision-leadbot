from flask import Flask,render_template,request,jsonify
from lead_engine import make_leads
app=Flask(__name__)
@app.get("/")
def index():return render_template("index.html")
@app.get("/health")
def health():return {"ok":True,"version":"Cihan Vision v3"}
@app.post("/api/route")
def route():
    data=request.get_json(silent=True) or {}
    try:lat=float(data["lat"]);lon=float(data["lon"])
    except Exception:return jsonify({"ok":False,"error":"Konum bilgisi okunamadı."}),400
    try:
        leads,summary=make_leads(lat,lon)
        return jsonify({"ok":True,"start":{"lat":lat,"lon":lon},"leads":leads,"summary":summary})
    except RuntimeError:return jsonify({"ok":False,"error":"İşletme verisi şu an alınamadı. 10-15 saniye sonra tekrar dene."}),503
    except Exception:
        app.logger.exception("route error")
        return jsonify({"ok":False,"error":"Rota oluşturulamadı."}),500
if __name__=="__main__":app.run(host="0.0.0.0",port=5000,debug=False)
