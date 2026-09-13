# [H] Vite before v2.9.13 vulnerable to directory traversal via crafted URL to victim's service

## Summary
Severity: High
Advisory: GHSA-mv48-hcvh-8jj8
CVE: CVE-2022-35204
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-08-19
Source: https://github.com/advisories/GHSA-mv48-hcvh-8jj8
Type: github-advisory

## Affected
- npm: `vite` — affected >=0 <2.9.13
- npm: `vite` — affected >=3.0.0-alpha.0 <3.0.0-beta.4

## Details
Vite before v2.9.13 was discovered to allow attackers to perform a directory traversal via a crafted URL to the victim's service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35204
- https://github.com/vitejs/vite/issues/8498
- https://github.com/vitejs/vite/commit/6851009e6725b17608113a5a63474280075cae1c
- https://github.com/vitejs/vite/commit/e109d64331d9fa57753832762c3573c3532a6947
- https://github.com/vitejs/vite
- https://github.com/vitejs/vite/releases/tag/v2.9.13
- https://github.com/vitejs/vite/releases/tag/v3.0.0-beta.4
