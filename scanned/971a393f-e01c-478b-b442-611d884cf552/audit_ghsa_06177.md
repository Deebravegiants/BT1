# [H] PDF.js: Arbitrary JavaScript execution upon opening a malicious PDF 

## Summary
Severity: High
Advisory: GHSA-hq66-cqwq-w95j
CVE: CVE-2026-16633
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-hq66-cqwq-w95j
Type: github-advisory

## Affected
- npm: `pdfjs-dist` — affected >=5.6.83 <6.2.108

## Details
### Impact

If PDF.js is used to load a malicious PDF, and PDF.js is configured with `enableScripting` set to true (which is the default value) and no CSP for disallowing script-src, unrestricted attacker-controlled JavaScript will be executed in the context of the hosting domain.

### Patches

### Workarounds
Set `enableScripting` to `false` or set a CSP.

## References
- https://github.com/mozilla/pdf.js/security/advisories/GHSA-hq66-cqwq-w95j
- https://bugzilla.mozilla.org/show_bug.cgi?id=2055885
- https://github.com/mozilla/pdf.js
