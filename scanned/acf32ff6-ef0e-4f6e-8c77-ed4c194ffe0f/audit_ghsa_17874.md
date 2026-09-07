# [H] Stored XSS in n8n Form Trigger allows Account Takeover via injected iframe and video/source

## Summary
Severity: High
Advisory: GHSA-hfmv-hhh3-43f2
CVE: CVE-2025-52478
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-hfmv-hhh3-43f2
Type: github-advisory

## Affected
- npm: `n8n` — affected >=1.77.0 <1.98.2

## Details
### Impact

A stored **Cross-Site Scripting (XSS)** vulnerability was identified in [n8n](https://github.com/n8n-io/n8n), specifically in the **Form Trigger** node's **HTML form element**. An authenticated attacker can inject malicious HTML via an `<iframe>` with a `srcdoc` payload that includes arbitrary JavaScript execution. The attacker can also inject malicious Javascript by using `<video>` coupled `<source>` using an `onerror` event.

While using `iframe` or a combination of `video` and `source` tag, this vulnerability allows for Account Takeover (ATO) by exfiltrating `n8n-browserId` and session cookies from authenticated users who visit a maliciously crafted form. Using these tokens and cookies, an attacker can impersonate the victim and change account details such as email addresses, enabling full control over the account—especially if 2FA is not enabled.

### Patches
The issue was addressed in [PR #16329](https://github.com/n8n-io/n8n/pull/16329). Users should upgrade to version >=1.98.2.

### Workarounds
Apart from updating to the fixed version, n8n instance administrators can:
- Configure a reverse proxy to **serve webhook requests from a different domain** [[docs](https://docs.n8n.io/hosting/configuration/configuration-examples/webhook-url/)].
- Disable or restrict use of the **Form Trigger node**, particularly the **HTML** element type.
- Use a Content Security Policy (CSP) to block execution of inline scripts and disallow use of `srcdoc`.

### References
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XSS_Prevention_Cheat_Sheet.html)
- [MDN: iframe `srcdoc` attribute](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#attr-srcdoc)
- [HTML: `onerror` attribute](https://html.spec.whatwg.org/multipage/webappapis.html#handler-onerror)

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-hfmv-hhh3-43f2
- https://nvd.nist.gov/vuln/detail/CVE-2025-52478
- https://github.com/n8n-io/n8n/pull/16329
- https://github.com/n8n-io/n8n/commit/7940384a85041a1890b1203d69c092c887312500
- https://github.com/n8n-io/n8n
