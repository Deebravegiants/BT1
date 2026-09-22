# [H] Jenkins JDepend Plugin vulnerable to XML external entity attacks

## Summary
Severity: High
Advisory: GHSA-jfg6-4gx3-3v7w
CVE: CVE-2025-64134
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-jfg6-4gx3-3v7w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jdepend` — affected >=0

## Details
Jenkins JDepend Plugin 1.3.1 and earlier includes an outdated version of JDepend Maven Plugin that does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to configure input files for the "Report JDepend" step to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64134
- https://github.com/jenkinsci/jdepend-plugin
- https://www.jenkins.io/security/advisory/2025-10-29/#SECURITY-2936
- http://www.openwall.com/lists/oss-security/2025/10/29/2
