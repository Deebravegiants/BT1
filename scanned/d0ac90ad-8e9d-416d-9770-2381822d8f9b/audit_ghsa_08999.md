# [M] CryptPad has a Sanitizer Bypass in Diffmarked.js that Allows Arbitrary HTML Injection and Potential XSS

## Summary
Severity: Medium
Advisory: GHSA-g2g4-47gv-p72v
CVE: CVE-2026-26028
CWE: CWE-116, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-g2g4-47gv-p72v
Type: github-advisory

## Affected
- npm: `cryptpad` — affected >=0

## Details
### Summary
CryptPad’s HTML sanitizer in Diffmarked.js can be bypassed due to incomplete filtering of restricted tags.
Because the sanitizer only validates the src attribute of `<iframe>` `<video>`, and `<audio>` elements,  and does not restrict other attributes, an attacker can inject arbitrary HTML through srcdoc. This completely defeats CryptPad’s intended bounce sandboxing and allows link injection or other interactive content inside user-controlled documents.

### Details
The sanitizer defines forbidden and restricted tags but treats <iframe> as “restricted” instead of “forbidden”:

https://github.com/cryptpad/cryptpad/blob/0dd3c1f53d56dffb06651b86ead6b9b387920173/www/common/diffMarked.js#L403-L407
The actual enforcement only checks the src attribute, nothing else:

https://github.com/cryptpad/cryptpad/blob/0dd3c1f53d56dffb06651b86ead6b9b387920173/www/common/diffMarked.js#L445-L449

Because only src is validated, adding a benign blob: src but malicious srcdoc results in unrestricted rendering.
### PoC

An attacker can embed arbitrary HTML, including clickable external links, images, or interactive content, completely bypassing CryptPad’s bounce mechanism and sanitization:

```html
<iframe src=blob: srcdoc="<a href=https://attacker.com target=_blank>CLICK ME</a>"></iframe>
```

Although CSP is strict, CryptPad exposes several same-origin gadgets that can execute attacker-controlled code.

For example, `jscolor.js` dynamically evaluates user-provided options:
https://github.com/cryptpad/cryptpad/blob/0dd3c1f53d56dffb06651b86ead6b9b387920173/www/common/jscolor.js#L65-L71

### Impact
Sanitizer bypass, HTML injection and potentially XSS.

## References
- https://github.com/cryptpad/cryptpad/security/advisories/GHSA-g2g4-47gv-p72v
- https://nvd.nist.gov/vuln/detail/CVE-2026-26028
- https://github.com/cryptpad/cryptpad
- https://github.com/cryptpad/cryptpad/releases/tag/2026.2.0
