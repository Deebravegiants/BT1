# [H] CVE-2018-15761

## Summary
Severity: High
Advisory: CVE-2018-15761
Aliases: GHSA-292x-hjr8-226f
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-19
Source: https://osv.dev/vulnerability/CVE-2018-15761
Type: osv

## Details
Cloud Foundry UAA release, versions prior to v64.0, and UAA, versions prior to 4.23.0, contains a validation error which allows for privilege escalation. A remote authenticated user may modify the url and content of a consent page to gain a token with arbitrary scopes that escalates their privileges.

## References
- https://www.cloudfoundry.org/blog/cve-2018-15761/
