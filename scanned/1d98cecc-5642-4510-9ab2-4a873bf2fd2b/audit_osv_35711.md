# [M] Frangoteam FUXA SCADA/HMI Authentication Bypass by Spoofing

## Summary
Severity: Medium
Advisory: CVE-2026-13207
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-13207
Type: osv

## Details
FUXA versions 1.3.1 and prior contain an authentication bypass vulnerability via dot-segment path normalization in the REST API. The API router fails to normalize dot-segment sequences before applying authentication middleware, allowing unauthenticated requests to access protected endpoints by prefixing paths with dot-segments such as /api/./users, /api/./roles, and /api/project/../users. These requests bypass authentication checks and return sensitive user and role data without credentials.

## References
- https://github.com/cisagov/CSAF/blob/develop/csaf_files/OT/white/2026/icsa-26-181-02.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13207.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13207
- https://www.cisa.gov/news-events/ics-advisories/icsa-26-181-02
- https://github.com/frangoteam/FUXA/releases
