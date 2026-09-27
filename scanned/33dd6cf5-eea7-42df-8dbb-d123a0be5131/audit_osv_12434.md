# [H] CVE-2018-1195

## Summary
Severity: High
Advisory: CVE-2018-1195
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-19
Source: https://osv.dev/vulnerability/CVE-2018-1195
Type: osv

## Details
In Cloud Controller versions prior to 1.46.0, cf-deployment versions prior to 1.3.0, and cf-release versions prior to 283, Cloud Controller accepts refresh tokens for authentication where access tokens are expected. This exposes a vulnerability where a refresh token that would otherwise be insufficient to obtain an access token, either due to lack of client credentials or revocation, would allow authentication.

## References
- https://www.cloudfoundry.org/blog/cve-2018-1195/
