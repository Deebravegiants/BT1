# [M] CVE-2021-3754

## Summary
Severity: Medium
Advisory: CVE-2021-3754
Aliases: GHSA-4vc8-pg5c-vg4x
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-08-26
Source: https://osv.dev/vulnerability/CVE-2021-3754
Type: osv

## Details
A flaw was found in keycloak where an attacker is able to register himself with the username same as the email ID of any existing user. This may cause trouble in getting password recovery email in case the user forgets the password.

## References
- https://access.redhat.com/security/cve/CVE-2021-3754
- https://bugzilla.redhat.com/show_bug.cgi?id=1999196
