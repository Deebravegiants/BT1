# [C] RT-Thread lwp_syscall.c sys_sigprocmask array index

## Summary
Severity: Critical
Advisory: CVE-2025-5866
CVSS: 9.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X)
Published: 2025-06-09
Source: https://osv.dev/vulnerability/CVE-2025-5866
Type: osv

## Details
A vulnerability classified as critical has been found in RT-Thread 5.1.0. This affects the function sys_sigprocmask of the file rt-thread/components/lwp/lwp_syscall.c. The manipulation of the argument how leads to improper validation of array index.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5866.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5866
- https://vuldb.com/?id.311625
- https://vuldb.com/?submit.584127
- https://github.com/RT-Thread/rt-thread/issues/10300
- https://vuldb.com/?ctiid.311625
