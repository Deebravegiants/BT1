# [M] CVE-2022-1516

## Summary
Severity: Medium
Advisory: CVE-2022-1516
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-05
Source: https://osv.dev/vulnerability/CVE-2022-1516
Type: osv

## Details
A NULL pointer dereference flaw was found in the Linux kernel’s X.25 set of standardized network protocols functionality in the way a user terminates their session using a simulated Ethernet card and continued usage of this connection. This flaw allows a local user to crash the system.

## References
- https://www.debian.org/security/2022/dsa-5173
- https://lists.debian.org/debian-lts-announce/2022/07/msg00000.html
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/?id=7781607938c8
- http://www.openwall.com/lists/oss-security/2022/06/19/1
