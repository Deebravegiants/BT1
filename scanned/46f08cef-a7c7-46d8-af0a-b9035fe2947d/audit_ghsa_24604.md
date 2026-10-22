# [M] Cloud Foundry vulnerable to Improper Certificate Validation

## Summary
Severity: Medium
Advisory: GHSA-rc2r-w8jv-vggp
CVE: CVE-2016-5016
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-rc2r-w8jv-vggp
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.0.0 <3.3.0.3
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.4.0 <3.4.2

## Details
Pivotal Cloud Foundry 239 and earlier, UAA (aka User Account and Authentication Server) 3.4.1 and earlier, UAA release 12.2 and earlier, PCF (aka Pivotal Cloud Foundry) Elastic Runtime 1.6.x before 1.6.35, and PCF Elastic Runtime 1.7.x before 1.7.13 does not validate if a certificate is expired.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5016
- https://github.com/cloudfoundry/uaa/commit/0a78612f981c541ad2d997e6a365f2a0b3e799d9
- https://github.com/cloudfoundry/uaa/commit/bc91ccd2029e8f1cea0c647f0c9aad4585f7a2c
- https://github.com/cloudfoundry/uaa/commit/f97049df1c6c03effda5049c41704ac831ff3925
- https://github.com/cloudfoundry/cf-release/releases/tag/v240
- https://github.com/cloudfoundry/uaa-release/releases/tag/v11.3
- https://github.com/cloudfoundry/uaa-release/releases/tag/v12.3
- https://github.com/cloudfoundry/uaa/releases/tag/2.7.4.6
- https://github.com/cloudfoundry/uaa/releases/tag/3.3.0.3
- https://github.com/cloudfoundry/uaa/releases/tag/3.4.2
- https://pivotal.io/security/cve-2016-5016
