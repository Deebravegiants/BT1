# [M] Flask-HTTPAuth invokes token verification callback when missing or empty token was given by client

## Summary
Severity: Medium
Advisory: GHSA-p44q-vqpr-4xmg
CVE: CVE-2026-34531
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-p44q-vqpr-4xmg
Type: github-advisory

## Affected
- PyPI: `Flask-HTTPAuth` — affected >=0 <4.8.1

## Details
## Summary

In a situation where the client makes a request to a token protected resource without passing a token, or passing an empty token, Flask-HTTPAuth would invoke the application's token verification callback function with the `token` argument set to an empty string. If the application had any users in its database with an empty string set as their token, then it could potentially authenticate the client request against any of those users.

## Notes

- This issue applies only to token authentication
- This issue applies only when the application verifies tokens by searching for them in a user database.
- This issue applies only if the application stores empty strings as user tokens when the user does not have an assigned token. It does not apply if the application sets those tokens to `NULL` instead.
- Tokens that are verified through cryptographic means (such as JWTs) are not affected by this issue.
- Basic and Digest authentication are not affected by this issue.

## Remediation

To protect against this issue, developers should make sure that no user in the user database has their `token` set to an empty string. If there are such users, change the value of those tokens to `NULL` instead.

Alternatively, developers can upgrade their projects to `Flask-HTTPAuth>=4.8.1`, which fixes this issue.

## References
- https://github.com/miguelgrinberg/Flask-HTTPAuth/security/advisories/GHSA-p44q-vqpr-4xmg
- https://nvd.nist.gov/vuln/detail/CVE-2026-34531
- https://github.com/miguelgrinberg/flask-httpauth/commit/b15ffe9e50e110d7174ccd944f642079e1dcf9ee
- https://github.com/miguelgrinberg/Flask-HTTPAuth
- https://github.com/miguelgrinberg/Flask-HTTPAuth/releases/tag/v4.8.1
- https://lists.debian.org/debian-lts-announce/2026/05/msg00049.html
