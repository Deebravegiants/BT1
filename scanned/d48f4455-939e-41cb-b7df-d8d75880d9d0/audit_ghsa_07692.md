# [M] Qwik City CSRF protection middleware does not work properly for content type header with parameters (eg. multipart/form-data)

## Summary
Severity: Medium
Advisory: GHSA-vm6g-8r4h-22x8
CVE: CVE-2026-25155
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-vm6g-8r4h-22x8
Type: github-advisory

## Affected
- npm: `@builder.io/qwik-city` — affected >=0 <1.12.0

## Details
### Summary
A typo in the regular expression within isContentType causes incorrect parsing of certain Content-Type headers.

### Impact
An attacker can bypass Qwik City’s Origin-based CSRF protections and perform forged form submissions, potentially causing unauthorized state changes.

## References
- https://github.com/QwikDev/qwik/security/advisories/GHSA-vm6g-8r4h-22x8
- https://nvd.nist.gov/vuln/detail/CVE-2026-25155
- https://github.com/QwikDev/qwik/commit/d70d7099b90b998f1aac7cedc21c67d87bac4c75
- https://github.com/QwikDev/qwik
