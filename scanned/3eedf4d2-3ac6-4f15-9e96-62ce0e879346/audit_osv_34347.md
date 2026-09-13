# [C] RT-Thread lwp_syscall.c csys_sendto null pointer dereference

## Summary
Severity: Critical
Advisory: CVE-2025-5867
CVSS: 9.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X)
Published: 2025-06-09
Source: https://osv.dev/vulnerability/CVE-2025-5867
Type: osv

## Details
A vulnerability classified as critical was found in RT-Thread 5.1.0. This vulnerability affects the function csys_sendto of the file rt-thread/components/lwp/lwp_syscall.c. The manipulation of the argument to leads to null pointer dereference.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5867.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5867
- https://vuldb.com/?id.311626
- https://vuldb.com/?submit.584129
- https://github.com/RT-Thread/rt-thread/issues/10299
- https://vuldb.com/?ctiid.311626
