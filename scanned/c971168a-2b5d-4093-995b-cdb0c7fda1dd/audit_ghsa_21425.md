# [M] Cross-site Scripting in Jenkins Naginator Plugin

## Summary
Severity: Medium
Advisory: GHSA-h8hf-hxx6-5g6v
CVE: CVE-2022-45382
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-h8hf-hxx6-5g6v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:naginator` — affected >=0 <1.18.2

## Details
Naginator Plugin 1.18.1 and earlier does not escape display names of source builds in builds that were triggered via Retry action.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to edit build display names.

Naginator Plugin 1.18.2 escapes display names of source builds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45382
- https://github.com/jenkinsci/naginator-plugin/commit/c335cdd1562333898216bbe137bbe2991c6a225f
- https://github.com/jenkinsci/naginator-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2946
- http://www.openwall.com/lists/oss-security/2022/11/15/4
