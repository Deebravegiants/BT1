# [H] Jenkins CCM Plugin vulnerable to Improper Restriction of XML External Entity Reference

## Summary
Severity: High
Advisory: GHSA-c4mp-h3m2-h5mc
CVE: CVE-2018-1000054
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-c4mp-h3m2-h5mc
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:ccm` — affected >=0 <3.2

## Details
Jenkins CCM Plugin 3.1 and earlier processes XML external entities in files it parses as part of the build process, allowing attackers with user permissions in Jenkins to extract secrets from the Jenkins master, perform server-side request forgery, or denial-of-service attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000054
- https://github.com/jenkinsci/ccm-plugin
- https://jenkins.io/security/advisory/2018-02-05
