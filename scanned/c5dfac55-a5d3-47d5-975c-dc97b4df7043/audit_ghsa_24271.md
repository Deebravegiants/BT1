# [H] Shell command injection in Liferay Portal

## Summary
Severity: High
Advisory: GHSA-97gm-mcv6-cphm
CVE: CVE-2010-5327
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-97gm-mcv6-cphm
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:portal-impl` — affected >=0 <6.2.11
- Maven: `com.liferay.portal:portal-service` — affected >=0 <6.2.11

## Details
Liferay Portal through 6.2.10 allows remote authenticated users to execute arbitrary shell commands via a crafted Velocity template.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-5327
- https://github.com/liferay/liferay-portal/commit/90c4e85a8f8135f069f3f05e4d54a77704769f91
- https://dev.liferay.com/web/community-security-team/known-vulnerabilities
- https://dev.liferay.com/web/community-security-team/known-vulnerabilities/-/asset_publisher/4AHAYapUm8Xc/content/lps-64547-remote-code-execution-and-privilege-escalation-in-templates
- https://issues.liferay.com/browse/LPE-14964
- https://issues.liferay.com/browse/LPS-64547
- https://issues.liferay.com/browse/LPS-7087
