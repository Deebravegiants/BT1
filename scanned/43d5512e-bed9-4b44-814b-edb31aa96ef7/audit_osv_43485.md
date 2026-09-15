# [H] Integer Underflow in DHCPv6 Sub-Option Parser in FreeRTOS-Plus-TCP

## Summary
Severity: High
Advisory: CVE-2026-7424
Aliases: GHSA-wrhm-c99p-2p8g
CVSS: 7.5 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-7424
Type: osv

## Details
Integer underflow in the DHCPv6 sub-option parser in FreeRTOS-Plus-TCP before V4.4.1 and V4.2.6 allows an adjacent network actor to corrupt the device's IPv6 address assignment, DNS configuration, and lease times, and to cause a denial of service (permanent IP task freeze requiring hardware reset) by sending a single crafted DHCPv6 packet.








The issue is present whenever DHCPv6 is enabled.








To mitigate this issue, users should upgrade to version V4.2.6 or V4.4.1 or newer.

## References
- https://aws.amazon.com/security/security-bulletins/2026-022-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7424.json
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/security/advisories/GHSA-wrhm-c99p-2p8g
- https://nvd.nist.gov/vuln/detail/CVE-2026-7424
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/releases/tag/V4.2.6
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/releases/tag/V4.4.1
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP
