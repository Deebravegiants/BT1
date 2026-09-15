# [H] CVE-2018-1089

## Summary
Severity: High
Advisory: CVE-2018-1089
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-09
Source: https://osv.dev/vulnerability/CVE-2018-1089
Type: osv

## Details
389-ds-base before versions 1.4.0.9, 1.3.8.1, 1.3.6.15 did not properly handle long search filters with characters needing escapes, possibly leading to buffer overflows. A remote, unauthenticated attacker could potentially use this flaw to make ns-slapd crash via a specially crafted LDAP request, thus resulting in denial of service.

## References
- https://access.redhat.com/errata/RHSA-2018:1364
- https://access.redhat.com/errata/RHSA-2018:1380
- https://lists.debian.org/debian-lts-announce/2018/07/msg00018.html
- http://www.securityfocus.com/bid/104137
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1089
