# [M] VTun-ng's failure to initialize encryption modules may cause reversion to plaintext

## Summary
Severity: Medium
Advisory: CVE-2025-54870
Aliases: GHSA-m3jc-27c6-2wrf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-08-05
Source: https://osv.dev/vulnerability/CVE-2025-54870
Type: osv

## Details
VTun-ng is a Virtual Tunnel over TCP/IP network. In versions 3.0.17 and below, failure to initialize encryption modules might cause reversion to plaintext due to insufficient error handling. The bug was first introduced in VTun-ng version 3.0.12. This is fixed in version 3.0.18. To workaround this issue, avoid blowfish-256.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54870.json
- https://github.com/leakingmemory/vtun-ng/security/advisories/GHSA-m3jc-27c6-2wrf
- https://nvd.nist.gov/vuln/detail/CVE-2025-54870
- https://github.com/leakingmemory/vtun-ng/commit/8c63982b6c487c52db1d56ab94c266f0bc857140
