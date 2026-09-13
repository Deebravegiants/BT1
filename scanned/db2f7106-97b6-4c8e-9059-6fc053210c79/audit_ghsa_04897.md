# [M] Netty: Unix-socket fd receive leaks descriptors when peer sends two at once

## Summary
Severity: Medium
Advisory: GHSA-w573-9ffj-6ff9
CVE: CVE-2026-45536
CWE: CWE-200, CWE-772
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-w573-9ffj-6ff9
Type: github-advisory

## Affected
- Maven: `io.netty:netty-transport-native-epoll` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-transport-native-kqueue` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-transport-native-kqueue` — affected >=0 <4.1.135.Final
- Maven: `io.netty:netty-transport-native-epoll` — affected >=0 <4.1.135.Final

## Details
netty_unix_socket_recvFd sets msg_control to `char control[CMSG_SPACE(sizeof(int))]` (line 940) — 24 bytes on 64-bit Linux. A peer-sent SCM_RIGHTS cmsg carrying two ints has cmsg_len = CMSG_LEN(8) = 24, which fits exactly with no MSG_CTRUNC, so the kernel installs both fds in the receiving process. The subsequent check `cmsg->cmsg_len == CMSG_LEN(sizeof(int))` (line 972, expected 20) fails, the branch that would read the fd is skipped, and neither installed fd is closed. The for(;;) loop calls recvmsg again (non-blocking → EAGAIN → Java maps to 0 → read loop exits normally), leaving two leaked fds per message. There is no MSG_CTRUNC handling. Reachable via Epoll/KQueue DomainSocketChannel when the application opts into DomainSocketReadMode.FILE_DESCRIPTORS (non-default).

## References
- https://github.com/netty/netty/security/advisories/GHSA-w573-9ffj-6ff9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45536
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
