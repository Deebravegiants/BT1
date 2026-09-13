# [M] Integer Underflow in ICMP Echo Reply Processing in FreeRTOS-Plus-TCP

## Summary
Severity: Medium
Advisory: CVE-2026-7423
Aliases: GHSA-7r59-2pgv-9v2r
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-7423
Type: osv

## Details
Integer underflow in the ICMP and ICMPv6 echo reply handlers in FreeRTOS-Plus-TCP before V4.4.1 and V4.2.6 allows an adjacent network user to cause a denial of service (device crash) when outgoing ping support is enabled, because header sizes are subtracted from a packet length field without validating the field is large enough, resulting in a heap out-of-bounds read of up to approximately 65KB.



To mitigate this issue, users should upgrade to the fixed version when available.

## References
- https://aws.amazon.com/security/security-bulletins/2026-021-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7423.json
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/security/advisories/GHSA-7r59-2pgv-9v2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-7423
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/releases/tag/V4.2.6
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/releases/tag/V4.4.1
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP
