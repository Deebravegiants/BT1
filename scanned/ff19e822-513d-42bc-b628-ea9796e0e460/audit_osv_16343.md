# [M] CVE-2019-5489

## Summary
Severity: Medium
Advisory: CVE-2019-5489
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-01-07
Source: https://osv.dev/vulnerability/CVE-2019-5489
Type: osv

## Details
The mincore() implementation in mm/mincore.c in the Linux kernel through 4.19.13 allowed local attackers to observe page cache access patterns of other processes on the same system, potentially allowing sniffing of secret information. (Fixing this affects the output of the fincore program.) Limited remote exploitation may be possible, as demonstrated by latency differences in accessing public files from an Apache HTTP Server.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00071.html
- https://lists.debian.org/debian-lts-announce/2019/06/msg00011.html
- https://seclists.org/bugtraq/2019/Jun/26
- https://lists.debian.org/debian-lts-announce/2019/06/msg00010.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00039.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00048.html
- https://access.redhat.com/errata/RHSA-2019:3309
- https://security.netapp.com/advisory/ntap-20190307-0001/
- https://access.redhat.com/errata/RHSA-2019:4159
- https://access.redhat.com/errata/RHSA-2019:3967
- https://access.redhat.com/errata/RHSA-2019:4057
- https://access.redhat.com/errata/RHSA-2019:4164
- https://access.redhat.com/errata/RHSA-2019:2809
- https://access.redhat.com/errata/RHSA-2019:4058
- https://arxiv.org/abs/1901.01161
- https://www.theregister.co.uk/2019/01/05/boffins_beat_page_cache/
- https://access.redhat.com/errata/RHSA-2019:2029
- https://access.redhat.com/errata/RHSA-2019:2043
- https://access.redhat.com/errata/RHSA-2019:4056
