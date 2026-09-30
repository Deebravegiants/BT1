# [M] CryptPad unbounded WebSocket frame flood

## Summary
Severity: Medium
Advisory: CVE-2025-51846
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2025-51846
Type: osv

## Details
CryptPad 2025.3.1 allows unbounded WebSocket frame flood. A remote, unauthenticated attacker can significantly degrade or deny service for all users of a CryptPad instance. Fixed in 2026.2.2.

## References
- https://github.com/cryptpad/cryptpad/pull/2239/changes/1e0c06ad8a0c5dab795f85f9730ec2693320c62e
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2026/va-26-119-01.json
- https://www.cve.org/CVERecord?id=CVE-2025-51846
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51846.json
- https://github.com/JohnPerifanis/cryptpad-cve-2025-51846-advisory/blob/main/README.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-51846
