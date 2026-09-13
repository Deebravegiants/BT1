# [C] RT-Thread Parameter lwp_syscall.c sys_select memory corruption

## Summary
Severity: Critical
Advisory: CVE-2025-5865
CVSS: 9.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X)
Published: 2025-06-09
Source: https://osv.dev/vulnerability/CVE-2025-5865
Type: osv

## Details
A vulnerability was found in RT-Thread 5.1.0. It has been rated as critical. Affected by this issue is the function sys_select of the file rt-thread/components/lwp/lwp_syscall.c of the component Parameter Handler. The manipulation of the argument timeout leads to memory corruption. The vendor explains, that "[t]he timeout parameter should be checked to check if it can be accessed correctly in kernel mode and used temporarily in kernel memory."

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5865.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5865
- https://vuldb.com/?id.311624
- https://vuldb.com/?submit.584124
- https://github.com/RT-Thread/rt-thread/issues/10298
- https://github.com/RT-Thread/rt-thread/issues/10298#issuecomment-2894952150
- https://vuldb.com/?ctiid.311624
