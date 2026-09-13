# [C] CVE-2019-16746

## Summary
Severity: Critical
Advisory: CVE-2019-16746
Aliases: A-145728612, ASB-A-145728612
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-24
Source: https://osv.dev/vulnerability/CVE-2019-16746
Type: osv

## Details
An issue was discovered in net/wireless/nl80211.c in the Linux kernel through 5.2.17. It does not check the length of variable elements in a beacon head, leading to a buffer overflow.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TASE2ESEZAER6DTZH3DJ4K2JNO46TVL7/
- https://usn.ubuntu.com/4186-1/
- https://usn.ubuntu.com/4209-1/
- https://usn.ubuntu.com/4210-1/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00009.html
- http://packetstormsecurity.com/files/155212/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://security.netapp.com/advisory/ntap-20191031-0005/
- https://usn.ubuntu.com/4183-1/
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://seclists.org/bugtraq/2019/Nov/11
- https://marc.info/?l=linux-wireless&m=156901391225058&w=2
