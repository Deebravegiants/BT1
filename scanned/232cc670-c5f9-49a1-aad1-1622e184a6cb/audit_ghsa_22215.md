# [H] CSRF vulnerability in Jenkins Sounds Plugin allow OS command execution

## Summary
Severity: High
Advisory: GHSA-x37x-3fw2-5qw2
CVE: CVE-2020-2098
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x37x-3fw2-5qw2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sounds` — affected >=0 <0.6

## Details
A cross-site request forgery vulnerability in Jenkins Sounds Plugin 0.5 and earlier allows attacker to execute arbitrary OS commands as the OS user account running Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2098
- https://github.com/jenkinsci/sounds-plugin
- https://jenkins.io/security/advisory/2020-01-15/#SECURITY-814
