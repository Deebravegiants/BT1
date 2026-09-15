# [C] RT-Thread ls1c CAN ls1c_can.h recvmsg stack-based overflow

## Summary
Severity: Critical
Advisory: CVE-2026-14605
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-14605
Type: osv

## Details
A vulnerability was identified in RT-Thread up to 5.0.2. Affected by this vulnerability is the function recvmsg in the library bsp/loongson/ls1cdev/libraries/ls1c_can.h of the component ls1c CAN Handler. Such manipulation leads to stack-based buffer overflow. Local access is required to approach this attack. The exploit is publicly available and might be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://github.com/RT-Thread/rt-thread/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14605.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14605
- https://vuldb.com/cve/CVE-2026-14605
- https://vuldb.com/submit/844580
- https://vuldb.com/vuln/376113
- https://github.com/RT-Thread/rt-thread/issues/11424
- https://vuldb.com/vuln/376113/cti
