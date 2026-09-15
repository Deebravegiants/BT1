# [H] CVE-2018-11083

## Summary
Severity: High
Advisory: CVE-2018-11083
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-05
Source: https://osv.dev/vulnerability/CVE-2018-11083
Type: osv

## Details
Cloud Foundry BOSH, versions v264 prior to v264.14.0 and v265 prior to v265.7.0 and v266 prior to v266.8.0 and v267 prior to v267.2.0, allows refresh tokens to be as access tokens when using UAA for authentication. A remote attacker with an admin refresh token given by UAA can be used to access BOSH resources without obtaining an access token, even if their user no longer has access to those resources.

## References
- https://www.cloudfoundry.org/blog/cve-2018-11083
