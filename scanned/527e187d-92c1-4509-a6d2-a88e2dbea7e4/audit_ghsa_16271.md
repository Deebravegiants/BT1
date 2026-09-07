# [M] fetch(url) leads to a memory leak in undici

## Summary
Severity: Medium
Advisory: GHSA-9f24-jqhm-jfcw
CVE: CVE-2024-24750
CWE: CWE-400, CWE-401
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-16
Source: https://github.com/advisories/GHSA-9f24-jqhm-jfcw
Type: github-advisory

## Affected
- npm: `undici` — affected >=6.0.0 <6.6.1

## Details
### Impact

Calling `fetch(url)` and not consuming the incoming body ((or consuming it very slowing) will lead to a memory leak. 

### Patches

Patched in v6.6.1

### Workarounds

Make sure to always consume the incoming body.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-9f24-jqhm-jfcw
- https://nvd.nist.gov/vuln/detail/CVE-2024-24750
- https://github.com/nodejs/undici/commit/87a48113f1f68f60aa09abb07276d7c35467c663
- https://github.com/nodejs/undici
- https://github.com/nodejs/undici/releases/tag/v6.6.1
- https://security.netapp.com/advisory/ntap-20240419-0006
