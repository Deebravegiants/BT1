# [M] RT-Thread lwp_syscall.c sys_getaddrinfo memory corruption

## Summary
Severity: Medium
Advisory: CVE-2026-14607
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-14607
Type: osv

## Details
A weakness has been identified in RT-Thread up to 5.0.2. This affects the function sys_getaddrinfo of the file components/lwp/lwp_syscall.c. Executing a manipulation of the argument ai_addr can lead to memory corruption. The attack can only be executed locally. The exploit has been made available to the public and could be used for attacks. The pull request to fix this issue awaits acceptance.

## References
- https://github.com/RT-Thread/rt-thread/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14607.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14607
- https://vuldb.com/cve/CVE-2026-14607
- https://vuldb.com/submit/844622
- https://vuldb.com/vuln/376115
- https://github.com/RT-Thread/rt-thread/issues/11428
- https://vuldb.com/vuln/376115/cti
- https://github.com/RT-Thread/rt-thread/pull/11454
