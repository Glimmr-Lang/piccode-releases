from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import time
import sys
import urllib.parse
import html

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        self._root = os.path.abspath(directory)
        super().__init__(*args, directory=self._root, **kwargs)

    def list_directory(self, path):
        try:
            files = os.listdir(path)
        except OSError:
            self.send_error(404, "Cannot list directory")
            return None

        files.sort(key=lambda a: a.lower())
        displaypath = urllib.parse.unquote(self.path)
        response = []

        response.append(f"<html><title>Index of {html.escape(displaypath)}</title>")
        response.append(f"<body><h2>Index of {html.escape(displaypath)}</h2><hr><pre>")

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

            response.append(
                f'<a href="{link_name}">{html.escape(display_name):50}</a> {size:10} bytes  {created}'
            )

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

