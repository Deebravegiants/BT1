# [C] DOMPurify vulnerable to tampering by prototype polution

## Summary
Severity: Critical
Advisory: GHSA-p3vf-v8qc-cwcr
CVE: CVE-2024-48910
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-10-31
Source: https://github.com/advisories/GHSA-p3vf-v8qc-cwcr
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <2.4.2

## Details
dompurify was vulnerable to prototype pollution

Fixed by https://github.com/cure53/DOMPurify/commit/d1dd0374caef2b4c56c3bd09fe1988c3479166dc

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-p3vf-v8qc-cwcr
- https://nvd.nist.gov/vuln/detail/CVE-2024-48910
- https://github.com/cure53/DOMPurify/commit/d1dd0374caef2b4c56c3bd09fe1988c3479166dc
- https://github.com/cure53/DOMPurify
- https://lists.debian.org/debian-lts-announce/2025/02/msg00010.html
