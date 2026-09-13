# [M] Exposure of Sensitive Information in OpenGoofy Hippo4j

## Summary
Severity: Medium
Advisory: GHSA-xg89-vvwp-9c27
CVE: CVE-2023-27095
CWE: CWE-200, CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-16
Source: https://github.com/advisories/GHSA-xg89-vvwp-9c27
Type: github-advisory

## Affected
- Maven: `cn.hippo4j:hippo4j-core` — affected >=0

## Details
Insecure Permissions vulnerability found in OpenGoofy Hippo4j v.1.4.3 allows attacker toescalate privileges via the AddUser method of the UserController function in Tenant Management module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27095
- https://github.com/opengoofy/hippo4j/issues/1061
