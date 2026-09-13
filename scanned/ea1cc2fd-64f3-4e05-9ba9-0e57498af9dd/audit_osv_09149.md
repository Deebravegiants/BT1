# [M] CVE-2016-8629

## Summary
Severity: Medium
Advisory: CVE-2016-8629
Aliases: GHSA-778x-2mqv-w6xw
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/CVE-2016-8629
Type: osv

## Details
Red Hat Keycloak before version 2.4.0 did not correctly check permissions when handling service account user deletion requests sent to the rest server. An attacker with service account authentication could use this flaw to bypass normal permissions and delete users in a separate realm.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0876.html
- http://www.securityfocus.com/bid/97392
- http://www.securitytracker.com/id/1038180
- https://access.redhat.com/errata/RHSA-2017:0872
- https://access.redhat.com/errata/RHSA-2017:0873
- https://bugzilla.redhat.com/show_bug.cgi?id=1388988
