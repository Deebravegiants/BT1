# [M] Missing hostname validation in Email Extension Plugin

## Summary
Severity: Medium
Advisory: GHSA-4qrj-99r6-jfrh
CVE: CVE-2020-2253
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4qrj-99r6-jfrh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:email-ext` — affected >=0 <2.76

## Details
Email Extension Plugin 2.75 and earlier does not perform hostname validation when connecting to the configured SMTP server. This lack of validation could be abused using a man-in-the-middle attack to intercept these connections.

Email Extension Plugin 2.76 validates the SMTP hostname when connecting via TLS by default. In Email Extension Plugin 2.75 and earlier, administrators can set the Java system property `mail.smtp.ssl.checkserveridentity` to `true` on startup to enable this protection. Alternatively, this protection can be enabled (or disabled in the new version) via the 'Advanced Email Properties' field in the plugin’s configuration in Configure System.

In case of problems, this protection can be disabled again by setting `mail.smtp.ssl.checkserveridentity` to `false` using either method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2253
- https://github.com/jenkinsci/email-ext-plugin/commit/ac039ba581f5946975a327709ff201b459900caa
- https://github.com/jenkinsci/email-ext-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1851
- http://www.openwall.com/lists/oss-security/2020/09/16/3
