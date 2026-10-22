# [C] CVE-2016-8218

## Summary
Severity: Critical
Advisory: CVE-2016-8218
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-13
Source: https://osv.dev/vulnerability/CVE-2016-8218
Type: osv

## Details
An issue was discovered in Cloud Foundry Foundation routing-release versions prior to 0.142.0 and cf-release versions 203 to 231. Incomplete validation logic in JSON Web Token (JWT) libraries can allow unprivileged attackers to impersonate other users to the routing API, aka an "Unauthenticated JWT signing algorithm in routing" issue.

## References
- https://www.cloudfoundry.org/cve-2016-8218/
