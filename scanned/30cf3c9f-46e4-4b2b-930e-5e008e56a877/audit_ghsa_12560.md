# [H] Jenkins Template Workflows Plugin vulnerable to Stored Cross-site Scripting

## Summary
Severity: High
Advisory: GHSA-62v2-xwh3-5gvx
CVE: CVE-2023-35146
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-62v2-xwh3-5gvx
Type: github-advisory

## Affected
- Maven: `org.jenkins.plugin.templateWorkflows:template-workflows` — affected >=0

## Details
Jenkins Template Workflows Plugin 41.v32d86a_313b_4a and earlier does not escape names of jobs used as buildings blocks for Template Workflow Job.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to create jobs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35146
- https://www.jenkins.io/security/advisory/2023-06-14/#SECURITY-3166
- http://www.openwall.com/lists/oss-security/2023/06/14/5
