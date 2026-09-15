# [H] CVE-2026-45832

## Summary
Severity: High
Advisory: CVE-2026-45832
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-45832
Type: osv

## Details
All V1 collection-level endpoints in ChromaDB's Python project pass None for the tenant and database to the authorization layer, allowing attackers to bypass authorization controls by using the V1 endpoints.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-45832.json
- https://access.redhat.com/security/cve/CVE-2026-45832
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45832.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45832
- https://www.hiddenlayer.com/sai-security-advisory/2026-06-chromadb-4
- https://bugzilla.redhat.com/show_bug.cgi?id=2488411
- https://github.com/chroma-core/chroma
