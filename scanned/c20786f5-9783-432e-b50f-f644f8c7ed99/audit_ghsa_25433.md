# [M] Cloud Foundry UAA Denial of Service through client token revocation endpoint

## Summary
Severity: Medium
Advisory: GHSA-j4p3-2m2h-cv5f
CVE: CVE-2017-8031
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-j4p3-2m2h-cv5f
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.6.0 <4.7.1
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.0.0 <4.5.3
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=0 <3.20.1

## Details
An issue was discovered in Cloud Foundry Foundation cf-release (all versions prior to v279) and UAA (30.x versions prior to 30.6, 45.x versions prior to 45.4, 52.x versions prior to 52.1). In some cases, the UAA allows an authenticated user for a particular client to revoke client tokens for other users on the same client. This occurs only if the client is using opaque tokens or JWT tokens validated using the check_token endpoint. A malicious actor could cause denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8031
- https://github.com/cloudfoundry/uaa/commit/1e2a746968cdac5b53164ca8955646e4257ecc7
- https://github.com/cloudfoundry/uaa/commit/20808046de8bbdc6fb2ac62829d4cc9d7a19f37
- https://github.com/cloudfoundry/uaa/commit/66166d17781aa257ff77a2fb7c69f72d0b611be
- https://github.com/cloudfoundry/uaa
- https://github.com/cloudfoundry/uaa/releases/tag/3.20.1
- https://github.com/cloudfoundry/uaa/releases/tag/4.5.3
- https://github.com/cloudfoundry/uaa/releases/tag/4.7.1
- https://web.archive.org/web/20200227134207/http://www.securityfocus.com/bid/101967
- https://www.cloudfoundry.org/cve-2017-8031
