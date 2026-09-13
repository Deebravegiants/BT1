# [M] CVE-2017-7562

## Summary
Severity: Medium
Advisory: CVE-2017-7562
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2017-7562
Type: osv

## Details
An authentication bypass flaw was found in the way krb5's certauth interface before 1.16.1 handled the validation of client certificates. A remote attacker able to communicate with the KDC could potentially use this flaw to impersonate arbitrary principals under rare and erroneous circumstances.

## References
- http://www.securityfocus.com/bid/100511
- https://access.redhat.com/errata/RHSA-2018:0666
- https://github.com/krb5/krb5/pull/694/commits/1de6ca2f2eb1fdbab51f1549a25a6903aefcc196
- https://github.com/krb5/krb5/pull/694/commits/50fe4074f188c2d4da0c421e96553acea8378db2
- https://github.com/krb5/krb5/pull/694/commits/b7af544e50a4d8291524f590e20dd44430bf627d
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7562
- https://github.com/krb5/krb5/pull/694
