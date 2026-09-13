# [C] RT-Thread lwp_syscall.c sys_recvfrom memory corruption

## Summary
Severity: Critical
Advisory: CVE-2025-5869
CVSS: 9.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X)
Published: 2025-06-09
Source: https://osv.dev/vulnerability/CVE-2025-5869
Type: osv

## Details
A vulnerability, which was classified as critical, was found in RT-Thread 5.1.0. Affected is the function sys_recvfrom of the file rt-thread/components/lwp/lwp_syscall.c. The manipulation of the argument from leads to memory corruption.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5869.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5869
- https://vuldb.com/?id.311628
- https://vuldb.com/?submit.584135
- https://github.com/RT-Thread/rt-thread/issues/10304
- https://vuldb.com/?ctiid.311628
