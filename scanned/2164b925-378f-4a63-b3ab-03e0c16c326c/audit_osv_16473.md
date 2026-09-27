# [M] CVE-2019-7317

## Summary
Severity: Medium
Advisory: CVE-2019-7317
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2019-7317
Type: osv

## Details
png_image_free in png.c in libpng 1.6.x before 1.6.37 has a use-after-free because png_image_free_function is called under png_safe_execute.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00084.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00044.html
- http://packetstormsecurity.com/files/152561/Slackware-Security-Advisory-libpng-Updates.html
- http://www.securityfocus.com/bid/108098
- https://access.redhat.com/errata/RHSA-2019:1265
- https://access.redhat.com/errata/RHSA-2019:1267
- https://access.redhat.com/errata/RHSA-2019:1269
- https://access.redhat.com/errata/RHSA-2019:1308
- https://access.redhat.com/errata/RHSA-2019:1309
- https://access.redhat.com/errata/RHSA-2019:1310
- https://access.redhat.com/errata/RHSA-2019:2494
- https://access.redhat.com/errata/RHSA-2019:2495
- https://access.redhat.com/errata/RHSA-2019:2585
- https://access.redhat.com/errata/RHSA-2019:2590
- https://access.redhat.com/errata/RHSA-2019:2592
- https://access.redhat.com/errata/RHSA-2019:2737
- https://lists.debian.org/debian-lts-announce/2019/05/msg00032.html
