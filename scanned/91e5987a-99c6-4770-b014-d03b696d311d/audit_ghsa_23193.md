# [M] Jenkins Badge Plugin cross-site scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3xjq-8j89-xrw9
CVE: CVE-2018-1000604
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3xjq-8j89-xrw9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:badge` — affected >=0 <1.5

## Details
A persisted cross-site scripting vulnerability exists in Jenkins Badge Plugin 1.4 and earlier in BadgeSummaryAction.java, HtmlBadgeAction.java that allows attackers able to control build badge content to define JavaScript that would be executed in another user's browser when that other user performs some UI actions. Badge Plugin 1.5 and newer sanitizes the provided HTML for display on the Jenkins web UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000604
- https://github.com/jenkinsci/badge-plugin/commit/63a7744cef33338e62898576a50bcc521d76ba9f
- https://github.com/jenkinsci/badge-plugin
- https://jenkins.io/security/advisory/2018-06-25/#SECURITY-906
