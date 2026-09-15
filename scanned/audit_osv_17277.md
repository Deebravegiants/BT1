# [M] CVE-2020-14302

## Summary
Severity: Medium
Advisory: CVE-2020-14302
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-14302
Type: osv

## Details
A flaw was found in Keycloak before 13.0.0 where an external identity provider, after successful authentication, redirects to a Keycloak endpoint that accepts multiple invocations with the use of the same "state" parameter. This flaw allows a malicious user to perform replay attacks.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1849584
