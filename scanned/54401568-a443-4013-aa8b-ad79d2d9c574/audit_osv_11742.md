# [M] CVE-2017-9461

## Summary
Severity: Medium
Advisory: CVE-2017-9461
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-06
Source: https://osv.dev/vulnerability/CVE-2017-9461
Type: osv

## Details
smbd in Samba before 4.4.10 and 4.5.x before 4.5.6 has a denial of service vulnerability (fd_open_atomic infinite loop with high CPU usage and memory consumption) due to wrongly handling dangling symlinks.

## References
- https://git.samba.org/?p=samba.git%3Ba=commit%3Bh=10c3e3923022485c720f322ca4f0aca5d7501310
- http://www.securityfocus.com/bid/99455
- https://access.redhat.com/errata/RHSA-2017:1950
- https://access.redhat.com/errata/RHSA-2017:2338
- https://access.redhat.com/errata/RHSA-2017:2778
- https://lists.debian.org/debian-lts-announce/2019/04/msg00013.html
- https://bugs.debian.org/864291
- https://bugzilla.samba.org/show_bug.cgi?id=12572
