# [M] Pivotal Cloud Foundry UAA XSS on UAA OpenID Connect check session iframe endpoint

## Summary
Severity: Medium
Advisory: GHSA-j97q-9xp9-g5fx
CVE: CVE-2018-1190
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-j97q-9xp9-g5fx
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.0.0 <3.20.2

## Details
An issue was discovered in these Pivotal Cloud Foundry products: all versions prior to cf-release v270, UAA v3.x prior to v3.20.2, and UAA bosh v30.x versions prior to v30.8 and all other versions prior to v45.0. A cross-site scripting (XSS) attack is possible in the clientId parameter of a request to the UAA OpenID Connect check session iframe endpoint used for single logout session management.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1190
- https://github.com/cloudfoundry/uaa/commit/96fe26711f8f8855d2994a531447f730afd61844
- https://github.com/cloudfoundry/uaa
- https://web.archive.org/web/20200227133214/http://www.securityfocus.com/bid/102427
- https://www.cloudfoundry.org/cve-2018-1190
