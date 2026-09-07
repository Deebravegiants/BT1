# [M] Jenkins IBM AppScan Plugin showed plain text password in job configuration form fields 

## Summary
Severity: Medium
Advisory: GHSA-65rj-cgrp-g65w
CVE: CVE-2019-10391
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-65rj-cgrp-g65w
Type: github-advisory

## Affected
- Maven: `com.hcl.security:ibm-application-security` — affected >=0 <1.2.5

## Details
Jenkins IBM Application Security on Cloud Plugin 1.2.4 and earlier transmitted configured passwords in plain text as part of job configuration forms, potentially resulting in their exposure. This plugin has bee deprecated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10391
- https://jenkins.io/security/advisory/2019-08-28/#SECURITY-1512
- http://www.openwall.com/lists/oss-security/2019/08/28/4
