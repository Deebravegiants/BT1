# [H] Jenkins Pipeline: Job Plugin vulnerable to stored Cross-site Scripting

## Summary
Severity: High
Advisory: GHSA-2wvv-phhw-qvmc
CVE: CVE-2023-32977
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-2wvv-phhw-qvmc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-job` — affected >=0 <1295.v395eb

## Details
Jenkins Pipeline: Job Plugin 1292.v27d8cc3e2602 and earlier does not escape the display name of the build that caused an earlier build to be aborted, when "Do not allow concurrent builds" is set.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to set build display names immediately.

The Jenkins security team is not aware of any plugins that allow the exploitation of this vulnerability, as the build name must be set before the build starts.
Pipeline: Job Plugin 1295.v395eb_7400005 escapes the display name of the build that caused an earlier build to be aborted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32977
- https://github.com/jenkinsci/workflow-job-plugin/commit/395eb740000509bff789c7f409c90f2a4a738821
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3042
