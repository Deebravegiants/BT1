# [M] CVE-2018-10912

## Summary
Severity: Medium
Advisory: CVE-2018-10912
Aliases: GHSA-h7j7-pw3v-3v3x
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-10912
Type: osv

## Details
keycloak before version 4.0.0.final is vulnerable to a infinite loop in session replacement. A Keycloak cluster with multiple nodes could mishandle an expired session replacement and lead to an infinite loop. A malicious authenticated user could use this flaw to achieve Denial of Service on the server.

## References
- https://access.redhat.com/errata/RHSA-2018:2428
- https://access.redhat.com/errata/RHSA-2019:0877
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10912
