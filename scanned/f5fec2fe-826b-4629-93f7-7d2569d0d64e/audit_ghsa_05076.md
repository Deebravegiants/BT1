# [M] Caddy: stripHTML template function bypass

## Summary
Severity: Medium
Advisory: GHSA-vcc4-2c75-vc9v
CVE: CVE-2026-52846
CWE: CWE-116
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-vcc4-2c75-vc9v
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2` — affected >=0 <2.11.4
- Go: `github.com/caddyserver/caddy` — affected >=0

## Details
### Summary
Caddy’s `stripHTML` template function cannot reliably remove all HTML tags from input strings. Certain malformed HTML, such as `<<>img src=x onerror=alert()>`, can bypass the tag-stripping logic, potentially leaving dangerous content in the output if it is later rendered as HTML. This may allow client-side XSS in cases where untrusted strings are rendered unsafely.

---

### Details
The vulnerability originates from `funcStripHTML` in:

[caddy/caddy/caddyhttp/templates/tplcontext.go](https://github.com/caddyserver/caddy/blob/77e9ce7404c4a76853e101a9f5687a929ee56654/modules/caddyhttp/templates/tplcontext.go)

```go
func (TemplateContext) funcStripHTML(s string) string {
    var buf bytes.Buffer
    var inTag, inQuotes bool
    var tagStart int
    for i, ch := range s {
        if inTag {
            if ch == '>' && !inQuotes {
                inTag = false
            } else if ch == '<' && !inQuotes {
                // false start
                buf.WriteString(s[tagStart:i])
                tagStart = i
            } else if ch == '"' {
                inQuotes = !inQuotes
            }
            continue
        }
        if ch == '<' {
            inTag = true
            tagStart = i
            continue
        }
        buf.WriteRune(ch)
    }
    if inTag {
        // false start
        buf.WriteString(s[tagStart:])
    }
    return buf.String()
}
```

### POC

Caddyfile setup

```
:8080 {
    root * ./site
    file_server
    templates
}
```

Template file (index.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>StripHTML Bypass Test</title>
</head>
<body>
    <p>{{ stripHTML "<<>img src=x onerror=alert('XSS')>" }}</p>
</body>
</html>
```

The payload exploits the false start branch to smuggle a literal < back into the output, then uses the following > to terminate the parser’s tag state, leaving a valid <img ...> tag behind.

Tested in v2.11.3

### Impact

Malformed HTML can bypass stripHTML, potentially allowing arbitrary HTML or JavaScript to be rendered if the output is used unsafely, leading to client-side XSS.

### AI Disclosure

AI assisted in writing the report description; however, the discovery of the issue has been done manually.

## References
- https://github.com/caddyserver/caddy/security/advisories/GHSA-vcc4-2c75-vc9v
- https://github.com/caddyserver/caddy
