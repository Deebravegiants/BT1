# [M]  Liferay DXP Vulnerable to Denial-of-service (DoS) in the Multi-Factor Authentication Module

## Summary
Severity: Medium
Advisory: GHSA-82j7-2h3j-hc7f
CVE: CVE-2021-29041
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-82j7-2h3j-hc7f
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.3.10.fp1

## Details
Denial-of-service (DoS) vulnerability in the Multi-Factor Authentication module in Liferay DXP 7.3 before fix pack 1 allows remote authenticated attackers to prevent any user from authenticating by (1) enabling Time-based One-time password (TOTP) on behalf of the other user or (2) modifying the other user's TOTP shared secret.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29041
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17131
- http://liferay.com
