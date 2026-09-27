# [H] CVE-2017-15134

## Summary
Severity: High
Advisory: CVE-2017-15134
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2017-15134
Type: osv

## Details
A stack buffer overflow flaw was found in the way 389-ds-base 1.3.6.x before 1.3.6.13, 1.3.7.x before 1.3.7.9, 1.4.x before 1.4.0.5 handled certain LDAP search filters. A remote, unauthenticated attacker could potentially use this flaw to make ns-slapd crash via a specially crafted LDAP request, thus resulting in denial of service.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00033.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00018.html
- http://www.securityfocus.com/bid/102790
- https://access.redhat.com/errata/RHSA-2018:0163
- https://bugzilla.redhat.com/show_bug.cgi?id=1531573
- https://pagure.io/389-ds-base/c/6aa2acdc3cad9
