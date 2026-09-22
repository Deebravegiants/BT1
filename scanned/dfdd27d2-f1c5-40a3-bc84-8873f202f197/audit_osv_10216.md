# [H] CVE-2017-14337

## Summary
Severity: High
Advisory: CVE-2017-14337
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-12
Source: https://osv.dev/vulnerability/CVE-2017-14337
Type: osv

## Details
When MISP before 2.4.80 is configured with X.509 certificate authentication (CertAuth) in conjunction with a non-MISP external user management ReST API, if an external user provides X.509 certificate authentication and this API returns an empty value, the unauthenticated user can be granted access as an arbitrary user.

## References
- https://github.com/MISP/MISP/commit/be111a470204a974c50682054c9c7d4b94396ed9
- https://www.circl.lu/advisory/CVE-2017-14337/
