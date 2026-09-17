# [H] CVE-2019-17666

## Summary
Severity: High
Advisory: CVE-2019-17666
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-17
Source: https://osv.dev/vulnerability/CVE-2019-17666
Type: osv

## Details
rtl_p2p_noa_ie in drivers/net/wireless/realtek/rtlwifi/ps.c in the Linux kernel through 5.3.6 lacks a certain upper-bound check, leading to a buffer overflow.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TRBP4O6D2SQ2NHCRHTJONGCZLWOIV5MN/
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00010.html
- https://access.redhat.com/errata/RHSA-2020:0328
- https://access.redhat.com/errata/RHSA-2020:0661
- https://security.netapp.com/advisory/ntap-20191031-0005/
- https://access.redhat.com/errata/RHSA-2020:0339
- https://twitter.com/nicowaisman/status/1184864519316758535
- https://access.redhat.com/errata/RHSA-2020:0543
- https://arstechnica.com/information-technology/2019/10/unpatched-linux-flaw-may-let-attackers-crash-or-compromise-nearby-devices/
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://usn.ubuntu.com/4184-1/
- https://usn.ubuntu.com/4185-1/
- https://usn.ubuntu.com/4186-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00064.html
- https://access.redhat.com/errata/RHSA-2020:0740
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://usn.ubuntu.com/4183-1/
- https://usn.ubuntu.com/4186-1/
- https://lkml.org/lkml/2019/10/16/1226
