# [M] Blind SQL Injection with privileged Cloud Foundry UAA endpoints

## Summary
Severity: Medium
Advisory: GHSA-cw9c-v3v2-99hm
CVE: CVE-2017-4974
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cw9c-v3v2-99hm
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=2.0.0 <2.7.4.15
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.0.0 <3.6.9
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.7.0 <3.9.11
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.10.0 <3.16.0

## Details
An issue was discovered in Cloud Foundry Foundation cf-release versions prior to v258; UAA release 2.x versions prior to v2.7.4.15, 3.6.x versions prior to v3.6.9, 3.9.x versions prior to v3.9.11, and other versions prior to v3.16.0; and UAA bosh release (uaa-release) 13.x versions prior to v13.13, 24.x versions prior to v24.8, and other versions prior to v30.1. An authorized user can use a blind SQL injection attack to query the contents of the UAA database, aka "Blind SQL Injection with privileged UAA endpoints."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-4974
- https://github.com/cloudfoundry/uaa/commit/01edea6337c8ddb2ab80906aa1254d3c1dc02fb
- https://github.com/cloudfoundry/uaa/commit/2dbeb9e93e076d71d7f0886dea9f77f23e0b8f3c
- https://github.com/cloudfoundry/uaa/commit/5dc5ca9176ed5baa870680d99f37e7e559dddc5
- https://github.com/cloudfoundry/uaa/commit/74b9b270787aa602196d59d58893c3a6e09816f9
- https://github.com/cloudfoundry/uaa/commit/b6d6526cb89120043d390bf0274cd062e9fc452
- https://github.com/cloudfoundry/uaa
- https://web.archive.org/web/20200227163823/http://www.securityfocus.com/bid/99254
- https://www.cloudfoundry.org/cve-2017-4974
