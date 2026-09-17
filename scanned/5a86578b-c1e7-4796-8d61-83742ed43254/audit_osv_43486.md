# [M] Out-of-Bounds Read in Router Advertisement Option Parser in FreeRTOS-Plus-TCP

## Summary
Severity: Medium
Advisory: CVE-2026-7425
Aliases: GHSA-gffr-xgjg-jh9j
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-7425
Type: osv

## Details
Insufficient option length validation in the IPv6 Router Advertisement parser in FreeRTOS-Plus-TCP before V4.2.6 and V4.4.1 allows an adjacent network actor to cause a denial of service (device crash) by sending a crafted Router Advertisement with a truncated PREFIX_INFORMATION option that is smaller than the expected structure size.



To mitigate this issue, users should upgrade to the fixed version when available.

## References
- https://aws.amazon.com/security/security-bulletins/2026-023-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7425.json
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/security/advisories/GHSA-gffr-xgjg-jh9j
- https://nvd.nist.gov/vuln/detail/CVE-2026-7425
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/releases/tag/V4.2.6
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/releases/tag/V4.4.1
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP
