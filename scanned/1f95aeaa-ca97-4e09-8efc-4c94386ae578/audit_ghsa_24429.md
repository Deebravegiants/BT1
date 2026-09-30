# [H] Cloud Foundry UAA accepts refresh token as access token on admin endpoints

## Summary
Severity: High
Advisory: GHSA-r4v8-9hgx-vm6m
CVE: CVE-2018-11047
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r4v8-9hgx-vm6m
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=0 <4.5.7
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.6.0 <4.7.6
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.8.0 <4.10.2
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.11.0 <4.12.4
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.13.0 <4.19.2

## Details
Cloud Foundry UAA, versions 4.19 prior to 4.19.2 and 4.12 prior to 4.12.4 and 4.10 prior to 4.10.2 and 4.7 prior to 4.7.6 and 4.5 prior to 4.5.7, incorrectly authorizes requests to admin endpoints by accepting a valid refresh token in lieu of an access token. Refresh tokens by design have a longer expiration time than access tokens, allowing the possessor of a refresh token to authenticate longer than expected. This affects the administrative endpoints of the UAA. i.e. /Users, /Groups, etc. However, if the user has been deleted or had groups removed, or the client was deleted, the refresh token will no longer be valid.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11047
- https://github.com/cloudfoundry/uaa/commit/0cd3c6fdd96206a1d6a376ac62e21e59e16cdcb1
- https://github.com/cloudfoundry/uaa/commit/2906057dae995024576ce6afdc20abd85569514
- https://github.com/cloudfoundry/uaa/commit/4cb1be404cf4a82e39cf2a6357aa17af8b33f2a1
- https://github.com/cloudfoundry/uaa/commit/4fa3e351ec0bface3b693810605905e29a9a8569
- https://github.com/cloudfoundry/uaa/commit/5d021e83ef143c64179d0da015aa76321ee40988
- https://github.com/cloudfoundry/uaa/commit/81aeb7a3aa048ea086c494f725d643e48dd9266
- https://github.com/cloudfoundry/uaa/commit/a1d523c7f150e56bf06df8b83ed1d416d6c1d3b
- https://github.com/cloudfoundry/uaa/commit/aba1fb5f18e0d628628b2d960fc6d0cc62d86f5
- https://github.com/cloudfoundry/uaa/commit/b37552d2bf084de059bc965b5ef5a45e64883904
- https://github.com/cloudfoundry/uaa/commit/bbbba5aec514ad88e7d1e168a2519c80229f02f
- https://github.com/cloudfoundry/uaa
- https://www.cloudfoundry.org/blog/cve-2018-11047
