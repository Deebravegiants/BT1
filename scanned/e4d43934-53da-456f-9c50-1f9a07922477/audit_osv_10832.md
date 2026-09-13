# [H] CVE-2017-3137

## Summary
Severity: High
Advisory: CVE-2017-3137
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2017-3137
Type: osv

## Details
Mistaken assumptions about the ordering of records in the answer section of a response containing CNAME or DNAME resource records could lead to a situation in which named would exit with an assertion failure when processing a response in which records occurred in an unusual order. Affects BIND 9.9.9-P6, 9.9.10b1->9.9.10rc1, 9.10.4-P6, 9.10.5b1->9.10.5rc1, 9.11.0-P3, 9.11.1b1->9.11.1rc1, and 9.9.9-S8.

## References
- http://www.securityfocus.com/bid/97651
- http://www.securitytracker.com/id/1038258
- http://www.securitytracker.com/id/1040195
- https://access.redhat.com/errata/RHSA-2017:1095
- https://access.redhat.com/errata/RHSA-2017:1105
- https://access.redhat.com/errata/RHSA-2017:1582
- https://access.redhat.com/errata/RHSA-2017:1583
- https://kb.isc.org/docs/aa-01466
- https://security.gentoo.org/glsa/201708-01
- https://security.netapp.com/advisory/ntap-20180802-0002/
- https://www.debian.org/security/2017/dsa-3854
