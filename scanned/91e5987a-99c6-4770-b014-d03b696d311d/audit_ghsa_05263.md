# [M] Jenkins does not encrypt secrets from POST config.xml submissions before storing them in job configurations

## Summary
Severity: Medium
Advisory: GHSA-m6wv-wh8g-64xc
CVE: CVE-2026-53442
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-m6wv-wh8g-64xc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.555.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.556 <2.568

## Details
Jenkins 2.567 and earlier, LTS 2.555.2 and earlier does not encrypt secrets from POST config.xml submissions before storing them in job configurations unencrypted in job config.xml files on the Jenkins controller where they can be viewed by users with Item/Extended Read permission, or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53442
- https://github.com/jenkinsci/jenkins/commit/037c2c30cd26b926ec9df3d1b60e16b80608edb4
- https://github.com/jenkinsci/jenkins/commit/206f0b565f0ce16b5162160ffb96f5dd59002ff7
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2026-06-10/#SECURITY-3744
