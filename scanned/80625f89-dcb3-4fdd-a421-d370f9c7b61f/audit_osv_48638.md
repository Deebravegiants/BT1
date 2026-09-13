# [H] CVE-2018-1058

## Summary
Severity: High
Advisory: CVE-2018-1058
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-02
Source: https://osv.dev/vulnerability/CVE-2018-1058
Type: osv

## Details
A flaw was found in the way Postgresql allowed a user to modify the behavior of a query for other users. An attacker with a user account could use this flaw to execute code with the permissions of superuser in the database. Versions 9.3 through 10 are affected.

## References
- https://www.postgresql.org/about/news/1834/
- http://www.securityfocus.com/bid/103221
- https://access.redhat.com/errata/RHSA-2018:2511
- https://access.redhat.com/errata/RHSA-2018:2566
- https://access.redhat.com/errata/RHSA-2018:3816
- https://usn.ubuntu.com/3589-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1547044
