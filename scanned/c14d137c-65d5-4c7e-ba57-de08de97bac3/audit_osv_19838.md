# [M] CVE-2021-26676

## Summary
Severity: Medium
Advisory: CVE-2021-26676
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-02-09
Source: https://osv.dev/vulnerability/CVE-2021-26676
Type: osv

## Details
gdhcp in ConnMan before 1.39 could be used by network-adjacent attackers to leak sensitive stack information, allowing further exploitation of bugs in gdhcp.

## References
- https://git.kernel.org/pub/scm/network/connman/connman.git/tree/ChangeLog
- https://kunnamon.io/tbone/
- https://lists.debian.org/debian-lts-announce/2021/02/msg00013.html
- https://security.gentoo.org/glsa/202107-29
- https://www.debian.org/security/2021/dsa-4847
- https://www.openwall.com/lists/oss-security/2021/02/08/2
- https://bugzilla.suse.com/show_bug.cgi?id=1181751
- https://git.kernel.org/pub/scm/network/connman/connman.git/commit/?id=58d397ba74873384aee449690a9070bacd5676fa
- https://git.kernel.org/pub/scm/network/connman/connman.git/commit/?id=a74524b3e3fad81b0fd1084ffdf9f2ea469cd9b1
