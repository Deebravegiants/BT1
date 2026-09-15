# [H] CVE-2017-7548

## Summary
Severity: High
Advisory: CVE-2017-7548
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-08-16
Source: https://osv.dev/vulnerability/CVE-2017-7548
Type: osv

## Details
PostgreSQL versions before 9.4.13, 9.5.8 and 9.6.4 are vulnerable to authorization flaw allowing remote authenticated attackers with no privileges on a large object to overwrite the entire contents of the object, resulting in a denial of service.

## References
- http://www.securitytracker.com/id/1039142
- https://access.redhat.com/errata/RHSA-2017:2677
- https://access.redhat.com/errata/RHSA-2017:2678
- https://security.gentoo.org/glsa/201710-06
- https://www.postgresql.org/about/news/1772/
- http://www.debian.org/security/2017/dsa-3935
- http://www.debian.org/security/2017/dsa-3936
- http://www.securityfocus.com/bid/100276
