from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return {"service": "auth-service", "status": "running"}

@app.route("/login", methods=["POST"])
def login():
    return {"message": "User authenticated successfully"}

@app.route("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
