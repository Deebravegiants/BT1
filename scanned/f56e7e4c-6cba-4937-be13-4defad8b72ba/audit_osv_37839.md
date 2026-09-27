# [M] pyload-ng: Authentication Bypass via Host Header Injection in ClickNLoad

## Summary
Severity: Medium
Advisory: CVE-2026-33511
Aliases: GHSA-g5j2-gxqh-x7pw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:L/SA:N)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2026-33511
Type: osv

## Details
pyLoad is a free and open-source download manager written in Python. From version 0.4.20 to before version 0.5.0b3.dev97, the local_check decorator in pyLoad's ClickNLoad feature can be bypassed by any remote attacker through HTTP Host header spoofing. This allows unauthenticated remote users to access localhost-restricted endpoints, enabling them to inject arbitrary downloads, write files to the storage directory, and execute JavaScript code. This issue has been patched in version 0.5.0b3.dev97.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33511.json
- https://github.com/pyload/pyload/security/advisories/GHSA-g5j2-gxqh-x7pw
- https://nvd.nist.gov/vuln/detail/CVE-2026-33511
