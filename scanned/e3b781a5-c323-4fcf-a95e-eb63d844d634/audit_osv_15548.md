# [H] CVE-2019-17050

## Summary
Severity: High
Advisory: CVE-2019-17050
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-30
Source: https://osv.dev/vulnerability/CVE-2019-17050
Type: osv

## Details
An issue was discovered in the Voyager package through 1.2.7 for Laravel. An attacker with admin privileges and Compass access can read or delete arbitrary files, such as the .env file. NOTE: a software maintainer has suggested a solution in which Compass is switched off in a production environment.

## References
- https://github.com/the-control-group/voyager/issues/4322
