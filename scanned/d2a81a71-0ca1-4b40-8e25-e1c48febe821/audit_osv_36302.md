# [C] FreeRDP has a heap-use-after-free in irp_thread_func

## Summary
Severity: Critical
Advisory: CVE-2026-22857
Aliases: GHSA-4gxq-jhq6-4cr8
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2026-22857
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.20.1, a heap use-after-free occurs in irp_thread_func because the IRP is freed by irp->Complete() and then accessed again on the error path. This vulnerability is fixed in 3.20.1.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.20.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22857.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-4gxq-jhq6-4cr8
- https://nvd.nist.gov/vuln/detail/CVE-2026-22857
