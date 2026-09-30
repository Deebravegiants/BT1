# [M] HTTP Response Splitting in WSO2 transport-http

## Summary
Severity: Medium
Advisory: GHSA-rvpc-w57p-q95f
CVE: CVE-2019-10797
CWE: CWE-113
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-rvpc-w57p-q95f
Type: github-advisory

## Affected
- Maven: `org.wso2.transport.http:org.wso2.transport.http.netty` — affected >=0 <6.3.1

## Details
Netty in WSO2 transport-http before v6.3.1 is vulnerable to HTTP Response Splitting due to HTTP Header validation being disabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10797
- https://snyk.io/vuln/SNYK-JAVA-ORGWSO2TRANSPORTHTTP-548944
