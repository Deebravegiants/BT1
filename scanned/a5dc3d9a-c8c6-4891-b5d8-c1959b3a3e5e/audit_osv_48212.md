# [H] CVE-2017-2636

## Summary
Severity: High
Advisory: CVE-2017-2636
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-07
Source: https://osv.dev/vulnerability/CVE-2017-2636
Type: osv

## Details
Race condition in drivers/tty/n_hdlc.c in the Linux kernel through 4.10.1 allows local users to gain privileges or cause a denial of service (double free) by setting the HDLC line discipline.

## References
- http://www.securityfocus.com/bid/96732
- https://access.redhat.com/errata/RHSA-2017:0931
- http://www.debian.org/security/2017/dsa-3804
- http://www.securitytracker.com/id/1037963
- https://access.redhat.com/errata/RHSA-2017:0932
- https://access.redhat.com/errata/RHSA-2017:0933
- https://access.redhat.com/errata/RHSA-2017:1125
- https://access.redhat.com/errata/RHSA-2017:1126
- https://access.redhat.com/errata/RHSA-2017:1232
- https://a13xp0p0v.github.io/2017/03/24/CVE-2017-2636.html
- https://access.redhat.com/errata/RHSA-2017:0892
- https://access.redhat.com/errata/RHSA-2017:0986
- https://access.redhat.com/errata/RHSA-2017:1233
- https://access.redhat.com/errata/RHSA-2017:1488
- https://bugzilla.redhat.com/show_bug.cgi?id=1428319
- http://www.openwall.com/lists/oss-security/2017/03/07/6
