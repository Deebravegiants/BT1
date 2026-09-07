# [C] Deserialization of Untrusted Data in Liferay Portal

## Summary
Severity: Critical
Advisory: GHSA-w7pm-cc4v-f3g8
CVE: CVE-2020-7961
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w7pm-cc4v-f3g8
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.kernel` — affected >=0 <4.35.3

## Details
Deserialization of Untrusted Data in Liferay Portal prior to 7.2.1 CE GA2 allows remote attackers to execute arbitrary code via JSON web services (JSONWS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7961
- https://github.com/liferay/liferay-portal
- https://github.com/liferay/liferay-portal/blob/7.2.1-ga2/portal-kernel/bnd.bnd
- https://portal.liferay.dev/learn/security/known-vulnerabilities
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/117954271
- https://research.checkpoint.com/2021/freakout-leveraging-newest-vulnerabilities-for-creating-a-botnet
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-7961
- http://packetstormsecurity.com/files/157254/Liferay-Portal-Java-Unmarshalling-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/158392/Liferay-Portal-Remote-Code-Execution.html
