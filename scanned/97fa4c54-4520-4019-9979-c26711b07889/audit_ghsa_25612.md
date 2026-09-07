# [M] Stored XSS in Jenkins CVS Plugin

## Summary
Severity: Medium
Advisory: GHSA-ghq2-m3pq-qf3p
CVE: CVE-2022-29037
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-ghq2-m3pq-qf3p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cvs` — affected >=0 <2.19.1

## Details
Jenkins CVS Plugin 2.19 and earlier does not escape the name and description of CVS Symbolic Name parameters on views displaying parameters, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29037
- https://github.com/jenkinsci/cvs-plugin/commit/043ef8801a7b3fbbf778245c3c7174d21e42efe2
- https://github.com/jenkinsci/cvs-plugin
- https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-2617
