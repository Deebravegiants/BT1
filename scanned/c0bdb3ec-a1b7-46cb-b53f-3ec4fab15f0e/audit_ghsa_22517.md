# [C] WSO2 API Manager vulnerable to SSRF

## Summary
Severity: Critical
Advisory: GHSA-jfgp-q2hg-w285
CVE: CVE-2020-13226
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jfgp-q2hg-w285
Type: github-advisory

## Affected
- Maven: `org.wso2.am:am-parent` — affected >=0

## Details
WSO2 API Manager 3.0.0 does not properly restrict outbound network access from a Publisher node, opening up the possibility of SSRF to this node's entire intranet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13226
- https://github.com/wso2/docs-apim/issues/816
- https://github.com/wso2/product-apim/issues/7677
- https://docs.wso2.com/display/Security/Security+Advisories
- https://docs.wso2.com/display/Security/WSO2+Security+Vulnerability+Management+Process
- https://github.com/wso2/product-apim
