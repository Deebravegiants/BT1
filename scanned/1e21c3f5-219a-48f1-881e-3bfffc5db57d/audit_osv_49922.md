# [C] CVE-2019-3689

## Summary
Severity: Critical
Advisory: CVE-2019-3689
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-19
Source: https://osv.dev/vulnerability/CVE-2019-3689
Type: osv

## Details
The nfs-utils package in SUSE Linux Enterprise Server 12 before and including version 1.3.0-34.18.1 and in SUSE Linux Enterprise Server 15 before and including version 2.1.1-6.10.2 the directory /var/lib/nfs is owned by statd:nogroup. This directory contains files owned and managed by root. If statd is compromised, it can therefore trick processes running with root privileges into creating/overwriting files anywhere on the system.

## References
- https://git.linux-nfs.org/?p=steved/nfs-utils.git%3Ba=commitdiff%3Bh=fee2cc29e888f2ced6a76990923aef19d326dc0e
- https://lists.debian.org/debian-lts-announce/2019/10/msg00026.html
- https://usn.ubuntu.com/4400-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00071.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00006.html
- https://bugzilla.suse.com/show_bug.cgi?id=1150733
