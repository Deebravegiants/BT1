# [H] SiYuan vulnerable to reflected XSS via SVG namespace prefix bypass in SanitizeSVG (getDynamicIcon, unauthenticated)

## Summary
Severity: High
Advisory: GHSA-73g7-86qr-jrg3
CVE: CVE-2026-34605
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-73g7-86qr-jrg3
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260330031106-f09953afc57a

## Details
### Summary

The `SanitizeSVG` function introduced in v3.6.0 to fix XSS in the unauthenticated `/api/icon/getDynamicIcon` endpoint can be bypassed by using namespace-prefixed element names such as `<x:script xmlns:x="http://www.w3.org/2000/svg">`. The Go HTML5 parser records the element's tag as `"x:script"` rather than `"script"`, so the tag check passes it through. The SVG is served with `Content-Type: image/svg+xml` and no Content Security Policy; when a browser opens the response directly, its XML parser resolves the prefix to the SVG namespace and executes the embedded script.

### Details

The `getDynamicIcon` route is registered without authentication:

```go
// kernel/server/serve.go
ginServer.Handle("GET", "/api/icon/getDynamicIcon", getDynamicIcon)
```

For type 8, the `content` query parameter is inserted directly into an SVG `<text>` element using `fmt.Sprintf` with no HTML encoding:

```go
// kernel/api/icon.go:579-584
return fmt.Sprintf(`
    <svg id="dynamic_icon_type8" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
        <path d="..."/>
        <text x="50%%" y="55%%" ...>%s</text>
    </svg>`, ..., content)
```

`SanitizeSVG` then parses the SVG with `github.com/88250/lute/html` and removes elements whose lowercased tag name matches a fixed list:

```go
// kernel/util/misc.go:249-252
tag := strings.ToLower(c.Data)
if tag == "script" || tag == "iframe" || tag == "object" || tag == "embed" ||
    tag == "foreignobject" || "animate" == tag || ... {
    n.RemoveChild(c)
```

The lute HTML parser stores the full qualified name including any namespace prefix in `Node.Data`. A payload like `<x:script xmlns:x="http://www.w3.org/2000/svg">` gets `Data = "x:script"`. The check `tag == "script"` is false, so the element is not removed and survives in the rendered output.

Confirmed with the same library version used by SiYuan:

```
html.Parse input:  <x:script xmlns:x="http://www.w3.org/2000/svg">alert(1)</x:script>
Node.Data result:  "x:script"   (not "script")
Removed by check:  false
Rendered output:   <x:script xmlns:x="http://www.w3.org/2000/svg">alert(1)</x:script>
```

The same bypass works for every element on the blocklist: `x:iframe`, `x:object`, `x:foreignObject`, etc.

The fix is to strip the namespace prefix before comparing:

```go
localName := tag
if i := strings.LastIndex(tag, ":"); i >= 0 {
    localName = tag[i+1:]
}
if localName == "script" || localName == "iframe" || ...
```

### PoC

```
GET /api/icon/getDynamicIcon?type=8&color=red&content=%3C%2Ftext%3E%3Cx%3Ascript%20xmlns%3Ax%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3Ealert%28document.domain%29%3C%2Fx%3Ascript%3E%3Ctext%3E HTTP/1.1
Host: 127.0.0.1:6806
```

Decoded `content` value:
```
</text><x:script xmlns:x="http://www.w3.org/2000/svg">alert(document.domain)</x:script><text>
```

The response is a valid SVG with the script element intact. Opening the URL directly in a browser triggers the alert, confirming script execution at the SiYuan server origin.

### Impact

Any user whose SiYuan instance is reachable over a local network is exposed. An attacker on the same network can craft the URL and share it. When the victim opens it in a browser, JavaScript executes at the `http://<siyuan-host>:6806` origin. Because SiYuan sets `Access-Control-Allow-Origin: *` and the script runs same-origin, it can call any API endpoint using the victim's existing session cookies, including endpoints to read all notes, export data, or modify settings. No authentication or prior access is needed to construct the payload.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-73g7-86qr-jrg3
- https://nvd.nist.gov/vuln/detail/CVE-2026-34605
- https://github.com/siyuan-note/siyuan/issues/17246
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.6.2
