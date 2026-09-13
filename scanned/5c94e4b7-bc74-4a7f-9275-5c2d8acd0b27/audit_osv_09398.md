# [M] CVE-2016-9778

## Summary
Severity: Medium
Advisory: CVE-2016-9778
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2016-9778
Type: osv

## Details
An error in handling certain queries can cause an assertion failure when a server is using the nxdomain-redirect feature to cover a zone for which it is also providing authoritative service. A vulnerable server could be intentionally stopped by an attacker if it was using a configuration that met the criteria for the vulnerability and if the attacker could cause it to accept a query that possessed the required attributes. Please note: This vulnerability affects the "nxdomain-redirect" feature, which is one of two methods of handling NXDOMAIN redirection, and is only available in certain versions of BIND. Redirection using zones of type "redirect" is not affected by this vulnerability. Affects BIND 9.9.8-S1 -> 9.9.8-S3, 9.9.9-S1 -> 9.9.9-S6, 9.11.0-9.11.0-P1.

## References
- http://www.securityfocus.com/bid/95388
- http://www.securitytracker.com/id/1037582
- https://kb.isc.org/article/AA-01442/
- https://security.gentoo.org/glsa/201708-01
- https://security.netapp.com/advisory/ntap-20180926-0005/
