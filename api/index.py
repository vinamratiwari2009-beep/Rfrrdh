from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "FF Guild API starter",
        "note": "This safe starter does not collect or forward account passwords."
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"success": True, "status": "ok"})

@app.route("/join", methods=["GET", "POST"])
def join():
    # Do not accept or forward account passwords to third-party token services.
    uid = request.args.get("uid") or (request.json or {}).get("uid") if request.is_json else request.args.get("uid")
    clan_id = request.args.get("guildid") or request.args.get("clan_id")

    if not uid or not clan_id:
        return jsonify({
            "success": False,
            "error": "uid and guildid are required"
        }), 400

    return jsonify({
        "success": False,
        "error": "Guild-join action is not configured.",
        "message": "Use an official, authorized game API and an account-safe authentication flow."
    }), 501
