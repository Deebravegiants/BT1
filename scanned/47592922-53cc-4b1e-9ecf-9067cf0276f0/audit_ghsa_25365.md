# [H] Cloud Foundry UAA reset password vulnerable to brute force attack

## Summary
Severity: High
Advisory: GHSA-fm5c-2rwc-887w
CVE: CVE-2016-3084
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fm5c-2rwc-887w
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=0 <3.3.0.1

## Details
The UAA reset password flow in Cloud Foundry release v236 and earlier versions, UAA release v3.3.0 and earlier versions, all versions of Login-server, UAA release v10 and earlier versions and Pivotal Elastic Runtime versions prior to 1.7.2 is vulnerable to a brute force attack due to multiple active codes at a given time. This vulnerability is applicable only when using the UAA internal user store for authentication. Deployments enabled for integration via SAML or LDAP are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3084
- https://github.com/cloudfoundry/uaa/commit/14350228989e2aee900b8d48a848293bb5152b6f
- https://github.com/cloudfoundry/uaa/commit/1d3ad7399d010f6a29dc3bf8139d792121301ab8
- https://github.com/cloudfoundry/uaa/commit/460627ed419e4227b10ff121248b3ffc009011a9
- https://github.com/cloudfoundry/uaa/commit/4a119d314744460ed56bcd740b2e913bf3f560c1
- https://github.com/cloudfoundry/uaa/commit/5c2377487bef9d716d5c8e5717df1fc00bc7b000
- https://github.com/cloudfoundry/uaa/commit/66132926f1bac0b878da5841be2f93fa5075d88f
- https://github.com/cloudfoundry/uaa/commit/b3834364ab573e9655348193780a56a602fe87b7
- https://github.com/cloudfoundry/uaa
- https://pivotal.io/security/cve-2016-3084
