# [M] Jenkins Static Analysis Utilities Plugin is vulnerable to Cross-site request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3v9f-4vff-rx42
CVE: CVE-2019-10307
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3v9f-4vff-rx42
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:analysis-core` — affected >=0 <1.96

## Details
Jenkins analysis-core Plugin has the capability to allow other plugins to display trend graphs for their static analysis results. analysis-core Plugin provides the configuration form for the default settings of each graph.

The configuration form and form submission handler did not perform a permission check, allowing attackers with Job/Read access to change the per-job graph configuration defaults for all users.

Additionally, the form submission handler did not require POST requests, resulting in a cross-site request forgery vulnerability.

analysis-core Plugin now requires Job/Configure permission and POST requests to configure the per-job graph defaults for all users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10307
- https://github.com/jenkinsci/analysis-core-plugin/commit/3d7a0c7907d831c58541508b893dcea2039809c5
- https://jenkins.io/security/advisory/2019-04-30/#SECURITY-1100
- https://web.archive.org/web/20200227073756/http://www.securityfocus.com/bid/108159
- http://www.openwall.com/lists/oss-security/2019/04/30/5
