# [H] CVE-2021-26675

## Summary
Severity: High
Advisory: CVE-2021-26675
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-09
Source: https://osv.dev/vulnerability/CVE-2021-26675
Type: osv

## Details
A stack-based buffer overflow in dnsproxy in ConnMan before 1.39 could be used by network adjacent attackers to execute code.

## References
- https://git.kernel.org/pub/scm/network/connman/connman.git/tree/ChangeLog
- https://kunnamon.io/tbone/
- https://lists.debian.org/debian-lts-announce/2021/02/msg00013.html
- https://security.gentoo.org/glsa/202107-29
- https://www.debian.org/security/2021/dsa-4847
- https://www.openwall.com/lists/oss-security/2021/02/08/2
- https://bugzilla.suse.com/show_bug.cgi?id=1181751
- https://git.kernel.org/pub/scm/network/connman/connman.git/commit/?id=e4079a20f617a4b076af503f6e4e8b0304c9f2cb
