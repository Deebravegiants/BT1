# [M] net: Stack Overflow with Ping (to own IP Address) via Shell

## Summary
Severity: Medium
Advisory: CVE-2026-1681
Aliases: GHSA-6fcc-8rwr-w7xx
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-1681
Type: osv

## Details
Issuing an ICMP ping via the `net ping` shell command to a device's own IPv4 address causes the network stack to recursively re-enter the input path on the same system work-queue stack. Because the destination is recognized as a local address, both the echo request and the resulting echo reply are processed inline before the current frame returns. The nested input-path frames exceed the work-queue stack and trigger a stack overflow.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1681.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-6fcc-8rwr-w7xx
- https://nvd.nist.gov/vuln/detail/CVE-2026-1681
- https://github.com/zephyrproject-rtos/zephyr
