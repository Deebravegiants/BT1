# [H] Issuer validation regression in Spring Cloud SSO Connector

## Summary
Severity: High
Advisory: GHSA-q4q2-93pw-qwgf
CVE: CVE-2018-1256
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-q4q2-93pw-qwgf
Type: github-advisory

## Affected
- Maven: `io.pivotal.spring.cloud:spring-cloud-sso-connector` — affected >=2.1.2.RELEASE <2.1.3.RELEASE

## Details
Spring Cloud SSO Connector, version 2.1.2, contains a regression which disables issuer validation in resource servers that are not bound to the SSO service. In PCF deployments with multiple SSO service plans, a remote attacker can authenticate to unbound resource servers which use this version of the SSO Connector with tokens generated from another service plan.

### Mitigation
Users of affected versions should apply the following mitigation:
* Releases that have fixed this issue include:</p><ul><li>Spring Cloud SSO Connector: 2.1.3</li></ul>
* Alternatively, you can perform <u>one</u> of the following workarounds:</p><ul><li>Bind your resource server to the SSO service plan via a service instance binding</li><li>Set “sso.connector.cloud.available=true” within your Spring application properties</li></ul>

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1256
- https://github.com/pivotal-cf/spring-cloud-sso-connector/commit/ef647a2acf2363c6018e8543d665ac8862593372
- https://pivotal.io/security/cve-2018-1256
