# [M] Jenkins Open Redirect vulnerability 

## Summary
Severity: Medium
Advisory: GHSA-8hmv-92wm-39ch
CVE: CVE-2025-27625
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-03-06
Source: https://github.com/advisories/GHSA-8hmv-92wm-39ch
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.492.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.493 <2.500

## Details
Various features in Jenkins redirect users to partially user-controlled URLs inside Jenkins. To prevent open redirect vulnerabilities, Jenkins limits redirections to safe URLs (neither absolute nor scheme-relative/network-path reference).

In Jenkins 2.499 and earlier, LTS 2.492.1 and earlier, redirects starting with backslash (`\`) characters are considered safe.

This allows attackers to perform phishing attacks by having users go to a Jenkins URL that will forward them to a different site, because browsers interpret these characters as part of scheme-relative redirects.

Jenkins 2.500, LTS 2.492.2 considers redirects to URLs starting with backslash (`\`) characters to be unsafe, rejecting such redirects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27625
- https://github.com/jenkinsci/jenkins/commit/4a9a3ecd08fc00d2f1c1125be789d8be24f02c9e
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2025-03-05/#SECURITY-3501
