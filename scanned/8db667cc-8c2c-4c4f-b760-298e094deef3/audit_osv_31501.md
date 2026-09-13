# [M] net: icmp: Out of bound memory read

## Summary
Severity: Medium
Advisory: CVE-2025-12899
Aliases: GHSA-c2vg-hj83-c2vg
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-01-30
Source: https://osv.dev/vulnerability/CVE-2025-12899
Type: osv

## Details
A flaw in Zephyr’s network stack allows an IPv4 packet containing ICMP type 128 to be misclassified as an ICMPv6 Echo Request. This results in an out-of-bounds memory read and creates a potential information-leak vulnerability in the networking subsystem.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12899.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-c2vg-hj83-c2vg
- https://nvd.nist.gov/vuln/detail/CVE-2025-12899
- https://github.com/zephyrproject-rtos/zephyr
