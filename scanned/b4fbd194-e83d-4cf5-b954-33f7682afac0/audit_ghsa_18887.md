# [H] Cross-Site Scripting (XSS) vulnerability through unescaped HTML attribute values

## Summary
Severity: High
Advisory: GHSA-52c5-vh7f-26fx
CVE: CVE-2025-64501
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2025-11-06
Source: https://github.com/advisories/GHSA-52c5-vh7f-26fx
Type: github-advisory

## Affected
- RubyGems: `prosemirror_to_html` — affected >=0 <0.2.1

## Details
### Impact

The prosemirror_to_html gem is vulnerable to Cross-Site Scripting (XSS) attacks through malicious HTML attribute values. While tag content is properly escaped, attribute values are not, allowing attackers to inject arbitrary JavaScript code.

**Who is impacted:**
- Any application using prosemirror_to_html to convert ProseMirror documents to HTML
- Applications that process user-generated ProseMirror content are at highest risk
- End users viewing the rendered HTML output could have malicious JavaScript executed in their browsers

**Attack vectors include:**
- `href` attributes with `javascript:` protocol: `<a href="javascript:alert(document.cookie)">`
- Event handlers: `<div onclick="maliciousCode()">`
- `onerror` attributes on images: `<img src=x onerror="alert('XSS')">`
- Other HTML attributes that can execute JavaScript

### Patches

A fix is currently in development. Users should upgrade to version **0.2.1** or later once released.

The patch escapes all HTML attribute values using `CGI.escapeHTML` to prevent injection attacks.

### Workarounds

Until a patched version is available, users can implement one or more of these mitigations:

1. **Sanitize output**: Pass the HTML output through a sanitization library like [Sanitize](https://github.com/rgrove/sanitize) or [Loofah](https://github.com/flavorjones/loofah):
```ruby
   html = ProsemirrorToHtml.render(document)
   safe_html = Sanitize.fragment(html, Sanitize::Config::RELAXED)
```

2. **Implement Content Security Policy (CSP)**: Add strict CSP headers to prevent inline JavaScript execution:
```
   Content-Security-Policy: default-src 'self'; script-src 'self'
```

3. **Input validation**: If possible, validate and sanitize ProseMirror documents before conversion to prevent malicious content from entering the system.

### References

- Vulnerable code: https://github.com/etaminstudio/prosemirror_to_html/blob/ea8beb32f6c37f29f042ba4155ccf18504da716e/lib/prosemirror_to_html.rb#L249
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [CWE-79: Improper Neutralization of Input During Web Page Generation](https://cwe.mitre.org/data/definitions/79.html)

## References
- https://github.com/etaminstudio/prosemirror_to_html/security/advisories/GHSA-52c5-vh7f-26fx
- https://nvd.nist.gov/vuln/detail/CVE-2025-64501
- https://github.com/etaminstudio/prosemirror_to_html/commit/4d59f94f550bcabeec30d298791bbdd883298ad8
- https://github.com/etaminstudio/prosemirror_to_html
- https://github.com/etaminstudio/prosemirror_to_html/blob/ea8beb32f6c37f29f042ba4155ccf18504da716e/lib/prosemirror_to_html.rb#L249
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/prosemirror_to_html/CVE-2025-64501.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/prosemirror_to_html/GHSA-vfpf-xmwh-8m65.yml
