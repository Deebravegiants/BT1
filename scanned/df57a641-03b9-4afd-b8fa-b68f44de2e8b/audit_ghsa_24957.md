# [M] Password stored in plain text by Jenkins Nomad Plugin

## Summary
Severity: Medium
Advisory: GHSA-5c2c-cvg6-ghjm
CVE: CVE-2021-21681
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5c2c-cvg6-ghjm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:nomad` — affected >=0 <0.7.5

## Details
Jenkins Nomad Plugin 0.7.4 and earlier stores the passwords to authenticate against the Docker registry unencrypted in the global `config.xml` file on the Jenkins controller as part of its worker templates configuration.

These passwords can be viewed by users with access to the Jenkins controller file system.

Jenkins Nomad Plugin 0.7.5 stores the Docker passwords encrypted. This change is effective after Jenkins restarts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21681
- https://github.com/jenkinsci/nomad-plugin/commit/d45123487d57c0e2a8a6869866b05362f690f511
- https://github.com/jenkinsci/nomad-plugin
- https://www.jenkins.io/security/advisory/2021-08-31/#SECURITY-2396
- http://www.openwall.com/lists/oss-security/2021/08/31/1
