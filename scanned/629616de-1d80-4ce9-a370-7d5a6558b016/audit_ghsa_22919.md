# [H] Jenkins SourceGear Vault plugin transmits credentials in plain text

## Summary
Severity: High
Advisory: GHSA-jrmf-xhr6-3428
CVE: CVE-2019-10435
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jrmf-xhr6-3428
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vault-scm-plugin` — affected >=0

## Details
Jenkins SourceGear Vault Plugin transmits configured credentials in plain text as part of job configuration forms, potentially resulting in their exposure. As of the publication of the advisory, there are no patches and the plugin is unmaintained.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10435
- https://github.com/jenkinsci/vault-scm-plugin
- https://jenkins.io/security/advisory/2019-10-01/#SECURITY-1524
- http://www.openwall.com/lists/oss-security/2019/10/01/2
