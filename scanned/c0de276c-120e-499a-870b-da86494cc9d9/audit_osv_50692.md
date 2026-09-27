# [M] CVE-2020-28941

## Summary
Severity: Medium
Advisory: CVE-2020-28941
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-19
Source: https://osv.dev/vulnerability/CVE-2020-28941
Type: osv

## Details
An issue was discovered in drivers/accessibility/speakup/spk_ttyio.c in the Linux kernel through 5.9.9. Local attackers on systems with the speakup driver could cause a local denial of service attack, aka CID-d41227544427. This occurs because of an invalid free when the line discipline is used more than once.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TITJQPYDWZ4NB2ONJWUXW75KSQIPF35T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZF4OGZPKTAJJXWHPIFP3LHEWWEMR5LPT/
- https://lists.debian.org/debian-lts-announce/2020/12/msg00015.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=d4122754442799187d5d537a9c039a49a67e57f1
- https://git.kernel.org/pub/scm/linux/kernel/git/gregkh/tty.git/commit/?h=tty-linus&id=d4122754442799187d5d537a9c039a49a67e57f1
- http://www.openwall.com/lists/oss-security/2020/11/19/5
- https://github.com/torvalds/linux/commit/d4122754442799187d5d537a9c039a49a67e57f1
- https://www.openwall.com/lists/oss-security/2020/11/19/3
