# [M] WSO2 products vulnerable to XML External Entity attack

## Summary
Severity: Medium
Advisory: GHSA-cr8h-fr86-8vfv
CVE: CVE-2023-6836
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-15
Source: https://github.com/advisories/GHSA-cr8h-fr86-8vfv
Type: github-advisory

## Affected
- Maven: `org.wso2.carbon.commons:org.wso2.carbon.ntask.core` — affected >=0 <4.7.24
- Maven: `org.wso2.am:wso2am` — affected >=0 <4.0.0-beta
- Maven: `org.wso2.carbon.registry:org.wso2.carbon.registry.extensions` — affected >=0 <4.7.31
- Maven: `org.wso2.carbon.event-processing:org.wso2.carbon.event.processor.core` — affected >=0 <2.2.12
- Maven: `org.wso2.carbon.analytics-common:org.wso2.carbon.event.input.adapter.core` — affected >=0 <5.2.23
- Maven: `org.wso2.carbon.governance:org.wso2.carbon.governance.common` — affected >=0 <4.8.13

## Details
Multiple WSO2 products have been identified as vulnerable due to an XML External Entity (XXE) attack abuses a widely available but rarely used feature of XML parsers to access sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6836
- https://github.com/wso2/carbon-analytics-common/commit/9478336859306d3ea13b25cb386f29c183707fde
- https://github.com/wso2/carbon-commons/commit/a08a587e3dd5146121a7b47a0fdd06ddbcd903f4
- https://github.com/wso2/carbon-event-processing/commit/e9953afd46a45f704de341a081f710cbdfa3f975
- https://github.com/wso2/carbon-governance/commit/ad36968d5a11d4fc35fa5cc4e8b5ae9a04e5bb4c
- https://github.com/wso2/carbon-registry/commit/738b2a0b3e5f118527da236467ed72d9fd9ce40e
- https://github.com/wso2/product-apim/commit/96e8f5d6566d57bbbb8d4257f6f55057a79d00b5
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2021/WSO2-2020-0716
