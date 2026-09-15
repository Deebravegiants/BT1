# [C] RT-Thread SWM341 CAN SWM341.h CAN_Receive stack-based overflow

## Summary
Severity: Critical
Advisory: CVE-2026-14606
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-14606
Type: osv

## Details
A security flaw has been discovered in RT-Thread up to 5.0.2. Affected by this issue is the function CAN_Receive in the library bsp/synwit/libraries/SWM341_CSL/CMSIS/DeviceSupport/SWM341.h of the component SWM341 CAN Handler. Performing a manipulation results in stack-based buffer overflow. The attack needs to be approached locally. The exploit has been released to the public and may be used for attacks. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://github.com/RT-Thread/rt-thread/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14606.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14606
- https://vuldb.com/cve/CVE-2026-14606
- https://vuldb.com/submit/844591
- https://vuldb.com/vuln/376114
- https://github.com/RT-Thread/rt-thread/issues/11425
- https://vuldb.com/vuln/376114/cti
