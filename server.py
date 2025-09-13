#!/usr/bin/env python3
import os, json, urllib.parse, http.cookies
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(__file__)
DATA_FILE = os.path.join(ROOT, "data", "content.json")
TEMPLATES = os.path.join(ROOT, "templates")
STATIC_DIR = os.path.join(ROOT, "static")

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

def read_body(rfile, length):
    return rfile.read(length).decode("utf-8")

def parse_form(body):
    return {k: v[0] for k, v in urllib.parse.parse_qs(body).items()}

def load_content():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_content(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class BeSoftHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index"):
            return self.send_template("index.html")
        if self.path == "/api/content":
            data = load_content()
            payload = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if self.path == "/admin":
            if not self.is_auth():
                return self.send_template("login.html")
            return self.send_template("admin.html")
        if self.path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie", "auth=; Path=/; Max-Age=0; HttpOnly")
            self.send_header("Location", "/")
            self.end_headers()
            return
        # static files
        if self.path.startswith("/static/"):
            return SimpleHTTPRequestHandler.do_GET(self)
        # 404
        self.send_error(404, "Not Found")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = read_body(self.rfile, length)
        if self.path == "/login":
            fields = parse_form(body)
            if fields.get("username")==ADMIN_USER and fields.get("password")==ADMIN_PASS:
                self.send_response(302)
                self.send_header("Set-Cookie", "auth=1; Path=/; HttpOnly")
                self.send_header("Location", "/admin")
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header("Location", "/admin")
                self.end_headers()
            return
        if self.path == "/admin/save":
            if not self.is_auth():
                self.send_response(302); self.send_header("Location","/admin"); self.end_headers(); return
            f = parse_form(body)
            data = load_content()
            data["hero"]["title"] = f.get("hero_title", data["hero"]["title"])
            data["hero"]["subtitle"] = f.get("hero_sub", data["hero"]["subtitle"])
            data["about"] = f.get("about", data["about"])
            try:
                data["services"] = json.loads(f.get("services","[]"))
                data["projects"] = json.loads(f.get("projects","[]"))
                data["team"] = json.loads(f.get("team","[]"))
            except json.JSONDecodeError:
                # ignore invalid JSON updates
                pass
            data["contact"]["address"] = f.get("addr", data["contact"]["address"])
            data["contact"]["email"] = f.get("email", data["contact"]["email"])
            data["contact"]["phone"] = f.get("phone", data["contact"]["phone"])
            save_content(data)
            self.send_response(302)
            self.send_header("Location","/admin")
            self.end_headers()
            return
        self.send_error(404, "Not Found")

    def send_template(self, name):
        path = os.path.join(TEMPLATES, name)
        if not os.path.isfile(path):
            self.send_error(404, "Missing template")
            return
        with open(path, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def translate_path(self, path):
        # serve /static/* from STATIC_DIR, else from ROOT
        p = super().translate_path(path)
        if path.startswith("/static/"):
            return os.path.join(ROOT, path.lstrip("/"))
        return p

    def is_auth(self):
        cookie = self.headers.get("Cookie","")
        c = http.cookies.SimpleCookie(cookie)
        return c.get("auth") is not None

if __name__ == "__main__":
    import socket
    PORT = int(os.getenv("PORT", "8000"))
    httpd = HTTPServer(("0.0.0.0", PORT), BeSoftHandler)
    print(f"BeSoft running on http://0.0.0.0:{PORT}")
    httpd.serve_forever()
