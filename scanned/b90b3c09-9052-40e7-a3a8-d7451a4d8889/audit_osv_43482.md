# [M] MAC Address Validation Bypass in FreeRTOS-Plus-TCP IPv4 and IPv6 Packet Processing

## Summary
Severity: Medium
Advisory: CVE-2026-7422
Aliases: GHSA-jpw4-6h59-62w9
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-7422
Type: osv

## Details
Insufficient packet validation in FreeRTOS-Plus-TCP before V4.2.6 and V4.4.1 allows an adjacent network actor to bypass all checksum and minimum-size validation by spoofing the Ethernet source MAC address to match one of the device's own registered endpoints, because the loopback detection mechanism skips all input validation for packets whose source MAC matches a local endpoint.



To mitigate this issue, users should upgrade to the fixed version when available.

## References
- https://aws.amazon.com/security/security-bulletins/2026-021-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7422.json
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/security/advisories/GHSA-jpw4-6h59-62w9
- https://nvd.nist.gov/vuln/detail/CVE-2026-7422
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/releases/tag/V4.2.6
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/releases/tag/V4.4.1
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP
