# [M] Insecure Default Initialization of Resource in Pivotal Spring Web Flow

## Summary
Severity: Medium
Advisory: GHSA-fg9w-cffm-pmh2
CVE: CVE-2017-4971
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fg9w-cffm-pmh2
Type: github-advisory

## Affected
- Maven: `org.springframework.webflow:spring-webflow` — affected >=2.4.0 <2.4.5

## Details
An issue was discovered in Pivotal Spring Web Flow through 2.4.4. Applications that do not change the value of the MvcViewFactoryCreator useSpringBinding property which is disabled by default (i.e., set to 'false') can be vulnerable to malicious EL expressions in view states that process form submissions but do not have a sub-element to declare explicit data binding property mappings.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-4971
- https://jira.spring.io/browse/SWF-1700
- https://pivotal.io/security/cve-2017-4971
- http://www.securityfocus.com/bid/98785
