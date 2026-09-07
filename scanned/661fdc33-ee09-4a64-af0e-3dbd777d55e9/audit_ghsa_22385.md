# [M] Jenkins SAML Plugin Session Fixation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4pjx-86pg-x4j5
CVE: CVE-2018-1000602
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4pjx-86pg-x4j5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:saml` — affected >=0 <1.0.7

## Details
A session fixation vulnerability exists in Jenkins SAML Plugin 1.0.6 and earlier in SamlSecurityRealm.java that allows unauthorized attackers to impersonate another users if they can control the pre-authentication session. SAML Plugin 1.0.7 invalidates the previous session during login and creates a new one.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000602
- https://github.com/jenkinsci/saml-plugin/commit/fd95d576bda64b278071428c7fbee03c02f843c0
- https://github.com/jenkinsci/saml-plugin
- https://jenkins.io/security/advisory/2018-06-25/#SECURITY-916
