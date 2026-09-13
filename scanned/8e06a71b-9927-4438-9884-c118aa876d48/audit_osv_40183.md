# [M] can: Local Denial of Service via SocketCAN Send

## Summary
Severity: Medium
Advisory: CVE-2026-5071
Aliases: GHSA-c3w6-x7m3-3c58
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-05-30
Source: https://osv.dev/vulnerability/CVE-2026-5071
Type: osv

## Details
The SocketCAN implementation validates the length of a user-provided buffer containing a socketcan_frame object using only a NET_ASSERT statement in zcan_sendto_ctx() before dereferencing it in socketcan_to_can_frame(). In production builds where assertions are disabled, a userspace application that controls the length passed to a sendto syscall can supply an incomplete or truncated frame, causing socketcan_to_can_frame() to dereference fields beyond the end of the buffer. This results in an out-of-bounds read that can cause denial-of-service crashes or, because the parsed frame contents are transmitted on the network, leak adjacent memory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5071.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-c3w6-x7m3-3c58
- https://nvd.nist.gov/vuln/detail/CVE-2026-5071
- https://github.com/zephyrproject-rtos/zephyr
