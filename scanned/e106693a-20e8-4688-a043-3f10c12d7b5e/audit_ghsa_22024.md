# [M] Stored XSS vulnerability in Jenkins Compact Columns Plugin

## Summary
Severity: Medium
Advisory: GHSA-x68x-wvm2-hqc8
CVE: CVE-2020-2195
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x68x-wvm2-hqc8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:compact-columns` — affected >=0 <1.12

## Details
Compact Columns Plugin 1.11 and earlier displays the unprocessed job description in tooltips.

This results in a stored cross-site scripting vulnerability that can be exploited by users with Job/Configure permission.

Compact Columns Plugin 1.12 applies the configured markup formatter to the job description shown in tooltips.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2195
- https://github.com/jenkinsci/compact-columns-plugin/commit/9a5fff4501568c85965940c0c1f620665c77fc27
- https://github.com/jenkinsci/compact-columns-plugin
- https://jenkins.io/security/advisory/2020-06-03/#SECURITY-1837
- http://www.openwall.com/lists/oss-security/2020/06/03/3
