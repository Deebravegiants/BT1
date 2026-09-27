# [H] CVE-2020-27815

## Summary
Severity: High
Advisory: CVE-2020-27815
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2020-27815
Type: osv

## Details
A flaw was found in the JFS filesystem code in the Linux Kernel which allows a local attacker with the ability to set extended attributes to panic the system, causing memory corruption or escalating privileges. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://lists.debian.org/debian-lts-announce/2021/02/msg00018.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://security.netapp.com/advisory/ntap-20210702-0004/
- https://www.debian.org/security/2021/dsa-4843
- https://bugzilla.redhat.com/show_bug.cgi?id=1897668%2C
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c61b3e4839007668360ed8b87d7da96d2e59fc6c
- http://www.openwall.com/lists/oss-security/2020/12/28/1
- https://www.openwall.com/lists/oss-security/2020/11/30/5%2C
- https://www.openwall.com/lists/oss-security/2020/12/28/1%2C
- http://www.openwall.com/lists/oss-security/2020/11/30/5
