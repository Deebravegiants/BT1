# [M] Cross-site Scripting in Nacos

## Summary
Severity: Medium
Advisory: GHSA-4gr7-qw2q-jxh6
CVE: CVE-2021-44667
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-4gr7-qw2q-jxh6
Type: github-advisory

## Affected
- Maven: `com.alibaba.nacos:nacos-common` — affected >=2.0.0-ALPHA.1 <2.1.0-BETA
- Maven: `com.alibaba.nacos:nacos-common` — affected >=0 <1.4.5

## Details
A Cross Site Scripting (XSS) vulnerability exists in Nacos prior to 1.4.5 and 2.1.0-BETA in auth/users via the (1) pageSize and (2) pageNo parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44667
- https://github.com/alibaba/nacos/issues/7359
- https://github.com/alibaba/nacos/pull/7364
- https://github.com/alibaba/nacos/pull/8980
- https://github.com/alibaba/nacos/commit/cd6d7e33b94f24814701f3faf8b632e5e85444c5
- https://github.com/alibaba/nacos/commit/d062fcafad0acd01673d404319526415a4af372b
- https://github.com/alibaba/nacos
