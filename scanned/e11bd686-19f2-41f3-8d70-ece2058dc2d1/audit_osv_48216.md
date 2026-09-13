# [M] CVE-2017-2668

## Summary
Severity: Medium
Advisory: CVE-2017-2668
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-06-22
Source: https://osv.dev/vulnerability/CVE-2017-2668
Type: osv

## Details
389-ds-base before versions 1.3.5.17 and 1.3.6.10 is vulnerable to an invalid pointer dereference in the way LDAP bind requests are handled. A remote unauthenticated attacker could use this flaw to make ns-slapd crash via a specially crafted LDAP bind request, resulting in denial of service.

## References
- http://www.securityfocus.com/bid/97524
- https://access.redhat.com/errata/RHSA-2017:0893
- https://access.redhat.com/errata/RHSA-2017:0920
- https://pagure.io/389-ds-base/issue/49220
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2668
