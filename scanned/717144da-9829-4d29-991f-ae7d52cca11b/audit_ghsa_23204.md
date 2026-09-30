# [C] Jenkins SSH Plugin user passwords for encrypted SSH keys stored in plaintext

## Summary
Severity: Critical
Advisory: GHSA-5gmf-8gh2-hhfp
CVE: CVE-2017-1000245
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5gmf-8gh2-hhfp
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:ssh` — affected >=0
- Maven: `org.jenkins-ci.plugins:ssh` — affected >=0 <2.5

## Details
The SSH Plugin stores credentials which allow jobs to access remote servers via the SSH protocol. User passwords and passphrases for encrypted SSH keys are stored in plaintext in a configuration file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000245
- https://jenkins.io/security/advisory/2017-07-10
