# [H] CVE-2016-2857

## Summary
Severity: High
Advisory: CVE-2016-2857
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:H)
Published: 2016-04-12
Source: https://osv.dev/vulnerability/CVE-2016-2857
Type: osv

## Details
The net_checksum_calculate function in net/checksum.c in QEMU allows local guest OS users to cause a denial of service (out-of-bounds heap read and crash) via the payload length in a crafted packet.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=362786f14a753d8a5256ef97d7c10ed576d6572b
- http://rhn.redhat.com/errata/RHSA-2016-2670.html
- http://rhn.redhat.com/errata/RHSA-2016-2671.html
- http://rhn.redhat.com/errata/RHSA-2016-2704.html
- http://rhn.redhat.com/errata/RHSA-2016-2705.html
- http://rhn.redhat.com/errata/RHSA-2016-2706.html
- http://rhn.redhat.com/errata/RHSA-2017-0083.html
- http://rhn.redhat.com/errata/RHSA-2017-0309.html
- http://rhn.redhat.com/errata/RHSA-2017-0334.html
- http://rhn.redhat.com/errata/RHSA-2017-0344.html
- http://rhn.redhat.com/errata/RHSA-2017-0350.html
- http://www.openwall.com/lists/oss-security/2016/03/03/9
- http://www.openwall.com/lists/oss-security/2016/03/07/3
- http://www.securityfocus.com/bid/84130
- http://www.ubuntu.com/usn/USN-2974-1
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
