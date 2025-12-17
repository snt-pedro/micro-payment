import shutil, tempfile, os

def _ensure_pip():
    if shutil.which("pip") is None:
        try:
            import ensurepip
            ensurepip.bootstrap()
        except Exception:
            import urllib.request
            url = "https://bootstrap.pypa.io/get-pip.py"
            with tempfile.TemporaryDirectory() as tmp:
                gp = os.path.join(tmp, "get-pip.py")
                urllib.request.urlretrieve(url, gp)
                subprocess.run([sys.executable, gp, "--upgrade"], check=True)