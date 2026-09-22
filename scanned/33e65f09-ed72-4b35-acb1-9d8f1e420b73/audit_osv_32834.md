# [H] espintcp: remove encap socket caching to avoid reference leak

## Summary
Severity: High
Advisory: CVE-2025-38097
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38097
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.1.141, >=6.2.0 <6.6.93, >=6.7.0 <6.12.31, >=6.13.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

espintcp: remove encap socket caching to avoid reference leak

The current scheme for caching the encap socket can lead to reference
leaks when we try to delete the netns.

The reference chain is: xfrm_state -> enacp_sk -> netns

Since the encap socket is a userspace socket, it holds a reference on
the netns. If we delete the espintcp state (through flush or
individual delete) before removing the netns, the reference on the
socket is dropped and the netns is correctly deleted. Otherwise, the
netns may not be reachable anymore (if all processes within the ns
have terminated), so we cannot delete the xfrm state to drop its
reference on the socket.

This patch results in a small (~2% in my tests) performance
regression.

A GC-type mechanism could be added for the socket cache, to clear
references if the state hasn't been used "recently", but it's a lot
more complex than just not caching the socket.

## References
- https://git.kernel.org/stable/c/028363685bd0b7a19b4a820f82dd905b1dc83999
- https://git.kernel.org/stable/c/74fd327767fb784c5875cf7c4ba1217f26020943
- https://git.kernel.org/stable/c/9cbca30102028f9ad3d2098f935c4368f581fd07
- https://git.kernel.org/stable/c/b58a295d10065960bcb9d60cb8ca6ead9837cd27
- https://git.kernel.org/stable/c/e4cde54b46a87231c77256a633be1bef62687d69
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38097.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38097
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
