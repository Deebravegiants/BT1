# [H] Gogs: Stored XSS via data URI in issue comments

## Summary
Severity: High
Advisory: GHSA-xrcr-gmf5-2r8j
CVE: CVE-2026-26022
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-xrcr-gmf5-2r8j
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.2

## Details
### Summary
A Stored Cross-site Scripting (XSS) vulnerability exists in the comment and issue description functionality. The application's HTML sanitizer explicitly allows `data:` URI schemes, enabling authenticated users to inject arbitrary JavaScript execution via malicious links.

### Details
The vulnerability is located in `internal/markup/sanitizer.go`. The application uses the `bluemonday` HTML sanitizer but explicitly weakens the security policy by allowing the `data` URL scheme:

```go
// internal/markup/sanitizer.go
func NewSanitizer() {
    sanitizer.init.Do(func() {
        // ...
        // Data URLs
        sanitizer.policy.AllowURLSchemes("data")
        // ...
    })
}
```

While the Markdown renderer rewrites relative links (mitigating standard Markdown `[link](data:...)` attacks), Gogs supports **Raw HTML** input. Raw HTML anchor tags bypass the Markdown parser's link rewriting and are processed directly by the sanitizer. Since the sanitizer is configured to allow `data:` URIs, payloads like `<a href="data:text/html...">` are rendered as-is.

### PoC
1.  Create a file named `exploit.md` in a repository.
2.  Add the following content (Raw HTML):
    ```html
    <a href="data:text/html;base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4=">Click me for XSS</a>
    ```
3.  Commit and push the file.
4.  Navigate to the file in the Gogs web interface.
5.  Click the "Click me for XSS" link.
6.  **Result:** An alert box with "XSS" appears, executing the JavaScript payload.

### Impact
This is a **Stored XSS** vulnerability. Any user who views the malicious comment and clicks the link will execute the attacker-supplied JavaScript in their browser context. This allows attackers to:
*   Steal authentication cookies and session tokens.
*   Perform arbitrary actions on behalf of the victim (e.g., modifying repositories, adding collaborators).
*   Redirect users to malicious sites.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-xrcr-gmf5-2r8j
- https://nvd.nist.gov/vuln/detail/CVE-2026-26022
- https://github.com/gogs/gogs/pull/8174
- https://github.com/gogs/gogs/commit/441c64d7bd8893b2f4e48660a8be3a7472e14291
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.2
