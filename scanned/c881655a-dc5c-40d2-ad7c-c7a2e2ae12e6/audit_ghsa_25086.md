# [H] Stored XSS vulnerability in Pipeline Maven Integration Plugin via unescaped display name

## Summary
Severity: High
Advisory: GHSA-hq2h-9mc3-h6w2
CVE: CVE-2020-2256
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hq2h-9mc3-h6w2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-maven` — affected >=0 <3.9.3

## Details
Pipeline Maven Integration Plugin 3.9.2 and earlier does not escape the upstream job’s display name shown as part of a build cause.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Job/Configure permission.

Pipeline Maven Integration Plugin 3.9.3 escapes upstream job names in build causes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2256
- https://github.com/jenkinsci/pipeline-maven-plugin/commit/78b8e6d49bffcc6b65064a882c03a2b4bb157230
- https://github.com/jenkinsci/pipeline-maven-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1976
- http://www.openwall.com/lists/oss-security/2020/09/16/3
