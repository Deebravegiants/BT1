# [M] CVE-2017-3136

## Summary
Severity: Medium
Advisory: CVE-2017-3136
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2017-3136
Type: osv

## Details
A query with a specific set of characteristics could cause a server using DNS64 to encounter an assertion failure and terminate. An attacker could deliberately construct a query, enabling denial-of-service against a server if it was configured to use the DNS64 feature and other preconditions were met. Affects BIND 9.8.0 -> 9.8.8-P1, 9.9.0 -> 9.9.9-P6, 9.9.10b1->9.9.10rc1, 9.10.0 -> 9.10.4-P6, 9.10.5b1->9.10.5rc1, 9.11.0 -> 9.11.0-P3, 9.11.1b1->9.11.1rc1, 9.9.3-S1 -> 9.9.9-S8.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00044.html
- http://www.securityfocus.com/bid/97653
- http://www.securitytracker.com/id/1038259
- https://access.redhat.com/errata/RHSA-2017:1095
- https://access.redhat.com/errata/RHSA-2017:1105
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03747en_us
- https://kb.isc.org/docs/aa-01465
- https://security.gentoo.org/glsa/201708-01
- https://security.netapp.com/advisory/ntap-20180802-0002/
- https://www.debian.org/security/2017/dsa-3854
