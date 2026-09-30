# [C] Vulnerability in Torpedo Query

## Summary
Severity: Critical
Advisory: GHSA-j7m2-58wv-9v79
CVE: CVE-2019-11343
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-j7m2-58wv-9v79
Type: github-advisory

## Affected
- Maven: `org.torpedoquery:org.torpedoquery` — affected >=0 <2.5.3

## Details
Torpedo Query before 2.5.3 mishandles the LIKE operator in ConditionBuilder.java, LikeCondition.java, and NotLikeCondition.java.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11343
- https://github.com/xjodoin/torpedoquery/commit/3c20b874fba9cc2a78b9ace10208de1602b56c3f
- https://github.com/xjodoin/torpedoquery
- https://github.com/xjodoin/torpedoquery/compare/v2.5.2...v2.5.3
