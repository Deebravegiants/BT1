# [H] Jenkins BART Plugin vulnerable to cross-site scripting (XSS)

## Summary
Severity: High
Advisory: GHSA-j923-26c2-qq9p
CVE: CVE-2022-45387
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-j923-26c2-qq9p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:bart` — affected >=0

## Details
Jenkins BART Plugin 1.0.3 and earlier does not escape the parsed content of build logs before rendering it on the Jenkins UI, resulting in a stored cross-site scripting (XSS) vulnerability. Currently, there are no known workarounds or patches available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45387
- https://github.com/jenkins-infra/update-center2/pull/658
- https://github.com/jenkinsci/bart-plugin
- https://github.com/jenkinsci/bart-plugin/blob/30d19e0ded8588c84601c7ffbcd0dd91c08ef945/src/main/java/org/jenkinsci/plugins/bart/LogParserBuildAction.java#L85
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2802
- http://www.openwall.com/lists/oss-security/2022/11/15/4
