# [M] CVE-2017-3135

## Summary
Severity: Medium
Advisory: CVE-2017-3135
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2017-3135
Type: osv

## Details
Under some conditions when using both DNS64 and RPZ to rewrite query responses, query processing can resume in an inconsistent state leading to either an INSIST assertion failure or an attempt to read through a NULL pointer. Affects BIND 9.8.8, 9.9.3-S1 -> 9.9.9-S7, 9.9.3 -> 9.9.9-P5, 9.9.10b1, 9.10.0 -> 9.10.4-P5, 9.10.5b1, 9.11.0 -> 9.11.0-P2, 9.11.1b1.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0276.html
- http://www.securityfocus.com/bid/96150
- http://www.securitytracker.com/id/1037801
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03747en_us
- https://kb.isc.org/docs/aa-01453
- https://security.gentoo.org/glsa/201708-01
- https://security.netapp.com/advisory/ntap-20180926-0005/
- https://www.debian.org/security/2017/dsa-3795
