# [M] CVE-2017-3140

## Summary
Severity: Medium
Advisory: CVE-2017-3140
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2017-3140
Type: osv

## Details
If named is configured to use Response Policy Zones (RPZ) an error processing some rule types can lead to a condition where BIND will endlessly loop while handling a query. Affects BIND 9.9.10, 9.10.5, 9.11.0->9.11.1, 9.9.10-S1, 9.10.5-S1.

## References
- http://www.securityfocus.com/bid/99088
- http://www.securitytracker.com/id/1038692
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03772en_us
- https://kb.isc.org/docs/aa-01495
- https://security.gentoo.org/glsa/201708-01
- https://security.netapp.com/advisory/ntap-20180926-0001/
