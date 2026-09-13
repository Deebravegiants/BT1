# [H] CVE-2018-19788

## Summary
Severity: High
Advisory: CVE-2018-19788
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-03
Source: https://osv.dev/vulnerability/CVE-2018-19788
Type: osv

## Details
A flaw was found in PolicyKit (aka polkit) 0.115 that allows a user with a uid greater than INT_MAX to successfully execute any systemctl command.

## References
- https://access.redhat.com/errata/RHSA-2019:2046
- https://access.redhat.com/errata/RHSA-2019:3232
- https://lists.debian.org/debian-lts-announce/2019/01/msg00021.html
- https://security.gentoo.org/glsa/201908-14
- https://security.netapp.com/advisory/ntap-20240816-0001/
- https://usn.ubuntu.com/3861-1/
- https://usn.ubuntu.com/3861-2/
- https://www.debian.org/security/2018/dsa-4350
- https://bugs.debian.org/915332
- https://gitlab.freedesktop.org/polkit/polkit/issues/74
