# [M] CVE-2016-8652

## Summary
Severity: Medium
Advisory: CVE-2016-8652
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2016-8652
Type: osv

## Details
The auth component in Dovecot before 2.2.27, when auth-policy is configured, allows a remote attackers to cause a denial of service (crash) by aborting authentication without setting a username.

## References
- http://dovecot.org/pipermail/dovecot-news/2016-December/000333.html
- http://www.openwall.com/lists/oss-security/2016/12/02/4
- http://www.openwall.com/lists/oss-security/2016/12/05/12
- http://www.securityfocus.com/bid/94639
