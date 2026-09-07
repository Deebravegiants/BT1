# [H] Stored XSS vulnerability in Jenkins DotCi Plugin

## Summary
Severity: High
Advisory: GHSA-q9g4-9fx4-v533
CVE: CVE-2022-41239
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-q9g4-9fx4-v533
Type: github-advisory

## Affected
- Maven: `com.groupon.jenkins-ci.plugins:DotCi` — affected >=0

## Details
DotCi Plugin 2.40.00 and earlier does not escape the GitHub user name parameter provided to commit notifications when displaying them in a build cause.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to submit crafted commit notifications to the `/githook/` endpoint (see also [SECURITY-2867](https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2867)).

This vulnerability is only exploitable in Jenkins 2.314 and earlier, LTS 2.303.1 and earlier. See the [LTS upgrade guide](https://www.jenkins.io/doc/upgrade-guide/2.303/#SECURITY-2452).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41239
- https://github.com/jenkinsci/DotCi
- https://plugins.jenkins.io/DotCi
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2884
- https://www.jenkins.io/security/plugins/#suspensions
