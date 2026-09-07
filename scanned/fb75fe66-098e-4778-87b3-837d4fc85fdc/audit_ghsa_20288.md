# [M] Server-side request forgery in Apache Dubbo

## Summary
Severity: Medium
Advisory: GHSA-gm48-83x4-84jg
CVE: CVE-2022-24969
CWE: CWE-601, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-10
Source: https://github.com/advisories/GHSA-gm48-83x4-84jg
Type: github-advisory

## Affected
- Maven: `org.apache.dubbo:dubbo` — affected >=2.5.0 <2.7.15
- Maven: `com.alibaba:dubbo` — affected >=2.5.0 <2.6.12

## Details
bypass CVE-2021-25640 > In Apache Dubbo prior to 2.6.12 and 2.7.15, the usage of parseURL method will lead to the bypass of the white host check which can cause open redirect or SSRF vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25640
- https://nvd.nist.gov/vuln/detail/CVE-2022-24969
- https://github.com/advisories/GHSA-gw4j-4229-q4px
- https://lists.apache.org/thread/1xbckc3467wfk5r7n2o44r2brdsbwxgr
