# [H] Cross-site Scripting in Jenkins GitLab Plugin

## Summary
Severity: High
Advisory: GHSA-f655-xhvm-cwp4
CVE: CVE-2022-34777
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-f655-xhvm-cwp4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gitlab-plugin` — affected >=0 <1.5.35

## Details
Jenkins GitLab Plugin 1.5.34 and earlier does not escape multiple fields inserted into the description of webhook-triggered builds, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission. GitLab Plugin 1.5.35 does not show user-provided fields in the build cause of webhook-triggered builds.

GitLab Plugin 1.5.35 does not show user-provided fields in the build cause of webhook-triggered builds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34777
- https://github.com/jenkinsci/gitlab-plugin/commit/24e9a99d8151b5345109ef12cddc1ab323baa4ee
- https://github.com/jenkinsci/gitlab-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2316
