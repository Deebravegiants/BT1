# [M] Jenkins's build authorization token is stored and displayed in plain text

## Summary
Severity: Medium
Advisory: GHSA-hxjg-2jvf-h3rx
CVE: CVE-2025-67638
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-hxjg-2jvf-h3rx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.529 <2.541
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.528.3

## Details
Jenkins 2.540 and earlier, LTS 2.528.2 and earlier does not mask build authorization tokens displayed on the job configuration form, increasing the potential for attackers to observe and capture them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67638
- https://github.com/jenkinsci/jenkins/commit/4710d65339251aaf1d1599f19545db99be24d981
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2025-12-10/#SECURITY-783
