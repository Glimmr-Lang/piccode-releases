from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import time
import sys
import urllib.parse
import html
from urllib.parse import unquote

PUBLIC_DIR = os.path.abspath(".")
IMG_DIR = os.path.abspath("../img")

STYLE = '''
<style>
table {
  border-collapse: collapse;
  width: 100%;
}

th, td {
  text-align: left;
}

tr:nth-child(odd) {
  background-color: #e8e8e8;
}
</style>
'''

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        self._root = os.path.abspath(directory)
        super().__init__(*args, directory=self._root, **kwargs)

    def translate_path(self, path):
        path = unquote(path)
        if path.startswith("/img/"):
            return os.path.join(IMG_DIR, path.removeprefix("/img/"))
        else:
            return os.path.join(PUBLIC_DIR, path.lstrip("/"))

    def list_directory(self, path):
        try:
            files = os.listdir(path)
        except OSError:
            self.send_error(404, "Cannot list directory")
            return None

        files.sort(key=lambda a: a.lower())
        displaypath = urllib.parse.unquote(self.path)
        response = []

        response.append(f"<html><head><title>Index of {html.escape(displaypath)}</title>" + STYLE + "</head>")
        response.append(f'<body><div style="display: flex"><img src="/img/appicon.png" width="7%" style="padding-right: 2%"/>')
        response.append(f"<h2>Index of {html.escape(displaypath)}</h2></div><hr><pre>")

        response.append(f"<table>")

        if self.path.strip("/") != "":
            parent_path = os.path.dirname(self.path.rstrip("/"))
            if not parent_path.endswith("/"):
                parent_path += "/"
            if not parent_path.startswith("/"):
                parent_path = "/" + parent_path
            response.append(
                f'<tr><td><a href="{html.escape(parent_path)}" style="padding-right: 25rem;">{"..."}</a></td></tr>'
            )


        for name in files:
            fullname = os.path.join(path, name)
            display_name = name + "/" if os.path.isdir(fullname) else name
            link_name = urllib.parse.quote(name)

            try:
                size = os.path.getsize(fullname)
                created = time.ctime(os.path.getctime(fullname))
            except Exception:
                size = "?"
                created = "?"

            response.append(f"<tr><td>")
            response.append(
                f'<a href="{link_name}" style="padding-right: 25rem;">{html.escape(display_name):50}</a> {size:10} bytes  {created}'
            )
            response.append(f"</td></tr>")


        response.append(f"</table>")
        response.append("</pre><hr></body></html>")
        encoded = "\n".join(response).encode('utf-8')

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fileserver.py /path/to/serve [port]")
        sys.exit(1)

    serve_dir = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080

    if not os.path.isdir(serve_dir):
        print(f"Error: {serve_dir} is not a valid directory.")
        sys.exit(1)

    os.chdir(serve_dir)  # optional: sets cwd to match the served dir

    server = HTTPServer(('', port), lambda *args, **kwargs: CustomHandler(*args, directory=serve_dir, **kwargs))
    print(f"Serving '{serve_dir}' at http://localhost:{port}")
    server.serve_forever()

