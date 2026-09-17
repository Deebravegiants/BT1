# [M] XML External Entity Reference in Jenkins Violations Plugin

## Summary
Severity: Medium
Advisory: GHSA-4598-wcg8-x56g
CVE: CVE-2022-45386
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-4598-wcg8-x56g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:violations` — affected >=0

## Details
Violations Plugin 0.7.11 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers to control XML input files for the 'Report Violations' post-build step to have agent processes parse a crafted file that uses external entities for extraction of secrets from the Jenkins agent or server-side request forgery.

Because Jenkins agent processes usually execute build tools whose input (source code, build scripts, etc.) is controlled externally, this vulnerability only has a real impact in very narrow circumstances: when attackers can control XML files, but are unable to change build steps, Jenkinsfiles, test code that gets executed on the agents, or similar.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45386
- https://github.com/jenkinsci/violations-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-766
- http://www.openwall.com/lists/oss-security/2022/11/15/4
