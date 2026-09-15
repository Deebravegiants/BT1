# [M] Cloud Foundry UAA Identity Zone Admin Privilege Escalation

## Summary
Severity: Medium
Advisory: GHSA-9frw-wmvq-5rrc
CVE: CVE-2017-8032
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-9frw-wmvq-5rrc
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=0 <3.6.13
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.7.0 <3.9.15
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.10.0 <3.20.0
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.0.0 <4.4.0

## Details
In Cloud Foundry cf-release versions prior to v264; UAA release all versions of UAA v2.x.x, 3.6.x versions prior to v3.6.13, 3.9.x versions prior to v3.9.15, 3.20.x versions prior to v3.20.0, and other versions prior to v4.4.0; and UAA bosh release (uaa-release) 13.x versions prior to v13.17, 24.x versions prior to v24.12. 30.x versions prior to 30.5, and other versions prior to v41, zone administrators are allowed to escalate their privileges when mapping permissions for an external provider.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8032
- https://github.com/cloudfoundry/uaa/commit/2c10c43f04cf31e9f8f496cd218bfc773dfc149
- https://github.com/cloudfoundry/uaa/commit/4e4d653edb6b8f68e12b7c415e07e068b1574b8
- https://github.com/cloudfoundry/uaa/commit/aa308c463eaec96704198c2686306c9fc42f126e
- https://github.com/cloudfoundry/uaa/commit/ea8c0ce7740a5d756d9f11964f6a6b4df54cc3b2
- https://github.com/cloudfoundry/uaa
- https://www.cloudfoundry.org/cve-2017-8032
