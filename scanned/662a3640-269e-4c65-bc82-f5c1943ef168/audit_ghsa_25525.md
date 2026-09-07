# [H] Improper handling of case sensitivity in Spring Framework

## Summary
Severity: High
Advisory: GHSA-g5mm-vmx4-3rg7
CVE: CVE-2022-22968
CWE: CWE-178
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-15
Source: https://github.com/advisories/GHSA-g5mm-vmx4-3rg7
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-context` — affected >=5.3.0 <5.3.19
- Maven: `org.springframework:spring-context` — affected >=0 <5.2.21.RELEASE

## Details
In Spring Framework versions 5.3.0 - 5.3.18, 5.2.0 - 5.2.20, and older unsupported versions, the patterns for disallowedFields on a DataBinder are case sensitive which means a field is not effectively protected unless it is listed with both upper and lower case for the first character of the field, including upper and lower case for the first character of all nested fields within the property path. Versions 5.3.19 and 5.2.21 contain a patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22968
- https://github.com/spring-projects/spring-framework/commit/833e750175349ab4fd502109a8b41af77e25cdea
- https://github.com/spring-projects/spring-framework/commit/a7cf19cec5ebd270f97a194d749e2d5701ad2ab7
- https://github.com/spring-projects/spring-framework
- https://security.netapp.com/advisory/ntap-20220602-0004
- https://tanzu.vmware.com/security/cve-2022-22968
- https://www.oracle.com/security-alerts/cpujul2022.html
