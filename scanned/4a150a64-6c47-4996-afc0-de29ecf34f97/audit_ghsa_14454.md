# [M] Hippo4j allows attacker to obtain sensitive info via ConfigVerifyController function of Tenant Management module

## Summary
Severity: Medium
Advisory: GHSA-h855-6hph-v363
CVE: CVE-2023-27096
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-27
Source: https://github.com/advisories/GHSA-h855-6hph-v363
Type: github-advisory

## Affected
- Maven: `cn.hippo4j:hippo4j-all` — affected >=0

## Details
Insecure Permissions vulnerability found in OpenGoofy Hippo4j v.1.4.3 allows attacker to obtain sensitive information via the ConfigVerifyController function of the Tenant Management module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27096
- https://github.com/opengoofy/hippo4j/issues/1060
- https://github.com/opengoofy/hippo4j
