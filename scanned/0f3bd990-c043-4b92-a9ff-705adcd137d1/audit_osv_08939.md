# [H] CVE-2016-7030

## Summary
Severity: High
Advisory: CVE-2016-7030
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-28
Source: https://osv.dev/vulnerability/CVE-2016-7030
Type: osv

## Details
FreeIPA uses a default password policy that locks an account after 5 unsuccessful authentication attempts, which allows remote attackers to cause a denial of service by locking out the account in which system services run on.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0001.html
- http://www.openwall.com/lists/oss-security/2017/01/02/5
- http://www.securityfocus.com/bid/94934
- https://pagure.io/freeipa?id=6f1d927467e7907fd1991f88388d96c67c9bff61
- https://bugzilla.redhat.com/show_bug.cgi?id=1370493
