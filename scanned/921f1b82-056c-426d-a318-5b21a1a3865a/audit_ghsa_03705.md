# [M] Moderate severity vulnerability that affects org.hswebframework.web:hsweb-commons

## Summary
Severity: Medium
Advisory: GHSA-qqv6-5w6p-3pgr
CVE: CVE-2018-20594
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-qqv6-5w6p-3pgr
Type: github-advisory

## Affected
- Maven: `org.hswebframework.web:hsweb-commons` — affected >=0

## Details
An issue was discovered in hsweb 3.0.4. It is a reflected XSS vulnerability due to the absence of type parameter checking in FlowableModelManagerController.java.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20594
- https://github.com/hs-web/hsweb-framework/issues/107
- https://github.com/hs-web/hsweb-framework/commit/b72a2275ed21240296c6539bae1049c56abb542f
- https://github.com/advisories/GHSA-qqv6-5w6p-3pgr
- https://github.com/hs-web/hsweb-framework
