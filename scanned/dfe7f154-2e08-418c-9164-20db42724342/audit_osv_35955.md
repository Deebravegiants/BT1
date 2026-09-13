# [H] pgvector buffer overflow via integer wraparound in IVFFlat index build on 32-bit systems

## Summary
Severity: High
Advisory: CVE-2026-18022
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-18022
Type: osv

## Details
Integer wraparound in IVFFlat index build in pgvector before 0.8.6 allows a database user to write data out-of-bounds, which could lead to arbitrary code execution. Only 32-bit systems are affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18022.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18022
- https://github.com/pgvector/pgvector/issues/1006
- https://github.com/pgvector/pgvector/commit/636a92a3395d2e036ffd40d07aeb400a708ae104
