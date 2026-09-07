# [H] DOMPurify allows tampering by prototype pollution

## Summary
Severity: High
Advisory: GHSA-mmhx-hmjr-r674
CVE: CVE-2024-45801
CWE: CWE-1321, CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2024-09-16
Source: https://github.com/advisories/GHSA-mmhx-hmjr-r674
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <2.5.4
- npm: `dompurify` — affected >=3.0.0 <3.1.3

## Details
It has been discovered that malicious HTML using special nesting techniques can bypass the depth checking added to DOMPurify in recent releases. It was also possible to use Prototype Pollution to weaken the depth check.

This renders dompurify unable to avoid XSS attack.

Fixed by https://github.com/cure53/DOMPurify/commit/1e520262bf4c66b5efda49e2316d6d1246ca7b21 (3.x branch) and https://github.com/cure53/DOMPurify/commit/26e1d69ca7f769f5c558619d644d90dd8bf26ebc (2.x branch).

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-mmhx-hmjr-r674
- https://nvd.nist.gov/vuln/detail/CVE-2024-45801
- https://github.com/cure53/DOMPurify/commit/1e520262bf4c66b5efda49e2316d6d1246ca7b21
- https://github.com/cure53/DOMPurify/commit/26e1d69ca7f769f5c558619d644d90dd8bf26ebc
- https://github.com/cure53/DOMPurify
