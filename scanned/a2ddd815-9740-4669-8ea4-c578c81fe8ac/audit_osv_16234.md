# [H] CVE-2019-3803

## Summary
Severity: High
Advisory: CVE-2019-3803
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-01-12
Source: https://osv.dev/vulnerability/CVE-2019-3803
Type: osv

## Details
Pivotal Concourse, all versions prior to 4.2.2, puts the user access token in a url during the login flow. A remote attacker who gains access to a user's browser history could obtain the access token and use it to authenticate as the user.

## References
- https://pivotal.io/security/cve-2019-3803
