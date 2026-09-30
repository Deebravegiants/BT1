# [M] XXE vulnerability on agents in Jenkins SourceMonitor Plugin

## Summary
Severity: Medium
Advisory: GHSA-h4wx-78p9-fwxw
CVE: CVE-2022-45396
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-h4wx-78p9-fwxw
Type: github-advisory

## Affected
- Maven: `com.thalesgroup.hudson.plugins:sourcemonitor` — affected >=0

## Details
SourceMonitor Plugin 0.2 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control XML input files for the 'Publish SourceMonitor results' post-build step to have agent processes parse a crafted file that uses external entities for extraction of secrets from the Jenkins agent or server-side request forgery.

Because Jenkins agent processes usually execute build tools whose input (source code, build scripts, etc.) is controlled externally, this vulnerability only has a real impact in very narrow circumstances: when attackers can control XML files, but are unable to change build steps, Jenkinsfiles, test code that gets executed on the agents, or similar.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45396
- https://github.com/jenkinsci/sourcemonitor-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2927
- http://www.openwall.com/lists/oss-security/2022/11/15/4
