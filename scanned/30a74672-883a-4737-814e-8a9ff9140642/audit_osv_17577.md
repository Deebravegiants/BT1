# [M] CVE-2020-1727

## Summary
Severity: Medium
Advisory: CVE-2020-1727
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-1727
Type: osv

## Details
A vulnerability was found in Keycloak before 9.0.2, where every Authorization URL that points to an IDP server lacks proper input validation as it allows a wide range of characters. This flaw allows a malicious to craft deep links that introduce further attack scenarios on affected clients.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1727
