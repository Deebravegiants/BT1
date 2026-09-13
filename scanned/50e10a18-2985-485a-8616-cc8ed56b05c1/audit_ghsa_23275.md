# [M] Improper Validation of Certificate with Host Mismatch in Jenkins Mailer Plugin

## Summary
Severity: Medium
Advisory: GHSA-6fr3-286q-q3cr
CVE: CVE-2020-2252
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6fr3-286q-q3cr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mailer` — affected >=1.32 <1.32.1
- Maven: `org.jenkins-ci.plugins:mailer` — affected >=1.30 <1.31.1
- Maven: `org.jenkins-ci.plugins:mailer` — affected >=0 <1.29.1

## Details
Jenkins Mailer Plugin prior to 1.32.1, 1.31.1, and 1.29.1 does not perform hostname validation when connecting to the configured SMTP server. This lack of validation could be abused using a man-in-the-middle attack to intercept these connections.

Mailer Plugin 1.32.1, 1.31.1, and 1.29.1 validates the SMTP hostname when connecting via TLS by default. In Mailer Plugin 1.32 and earlier, administrators can set the Java system property mail.smtp.ssl.checkserveridentity to true on startup to enable this protection.

In case of problems, this protection can be disabled again by setting the Java system property mail.smtp.ssl.checkserveridentity to false on startup.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2252
- https://github.com/jenkinsci/mailer-plugin/commit/e1893c6d105669f134ee5c5212ef9f3944d7d00d
- https://github.com/CVEProject/cvelist/blob/16860a328d970faa6e4350b0fa446f64a52e52ca/2020/2xxx/CVE-2020-2252.json
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1813
- http://www.openwall.com/lists/oss-security/2020/09/16/3
