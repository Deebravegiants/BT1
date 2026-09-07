# [H] Next.js Directory Traversal Vulnerability

## Summary
Severity: High
Advisory: GHSA-3f5c-4qxj-vmpf
CVE: CVE-2017-16877
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2017-12-05
Source: https://github.com/advisories/GHSA-3f5c-4qxj-vmpf
Type: github-advisory

## Affected
- npm: `next` — affected >=1.0.0 <2.4.1

## Details
Next.js before 2.4.1 has directory traversal under the `/_next` and `/static` request namespace, allowing attackers to obtain sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16877
- https://github.com/vercel/next.js/commit/02fe7cf63f6265d73bdaf8bc50a4f2fb539dcd00
- https://github.com/zeit/next.js
- https://github.com/zeit/next.js/releases/tag/2.4.1
