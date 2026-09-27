# [M] WSO2 API Manager allows attackers to change the API rating

## Summary
Severity: Medium
Advisory: GHSA-w7rx-824v-rgx5
CVE: CVE-2023-6835
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-12-15
Source: https://github.com/advisories/GHSA-w7rx-824v-rgx5
Type: github-advisory

## Affected
- Maven: `org.wso2.carbon.apimgt:forum` — affected >=0

## Details
Multiple WSO2 products have been identified as vulnerable due to lack of server-side input validation in the Forum feature, API rating could be manipulated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6835
- https://github.com/wso2/carbon-apimgt/commit/2e9591b72bc286dfcd22b57768e984d867c902ba
- https://github.com/wso2/carbon-apimgt
- https://github.com/wso2/carbon-apimgt/blob/81e0c0b8ed0bd2dace1e9006be21acbb731c835e/components/forum/org.wso2.carbon.forum/src/main/java/org/wso2/carbon/forum/registry/RegistryForumManager.java#L762
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2021/WSO2-2021-1357
