# [M] Jenkins Open Redirect Through Newline/Tab Characters in Redirect URL

## Summary
Severity: Medium
Advisory: GHSA-463r-5m89-4xfr
CVE: CVE-2026-53437
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-463r-5m89-4xfr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.555.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.556 <2.568

## Details
Jenkins 2.567 and earlier, LTS 2.555.2 and earlier improperly determines that a redirect URL after login is legitimately pointing to Jenkins when it contains tab or newline characters between `//`, allowing attackers to perform phishing attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53437
- https://github.com/jenkinsci/jenkins/commit/b32f2f27a82ed187a34f55b05edcc4a83563d574
- https://github.com/jenkinsci/jenkins/commit/8ef52891b07eb639b38271e4bab5dab3c0f10fda
- https://www.jenkins.io/security/advisory/2026-06-10/#SECURITY-3711+3755
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53437.json
- https://github.com/jenkinsci/jenkins
- https://bugzilla.redhat.com/show_bug.cgi?id=2487544
- https://access.redhat.com/security/cve/CVE-2026-53437
- https://access.redhat.com/errata/RHSA-2026:60259
- https://access.redhat.com/errata/RHSA-2026:60256
- https://access.redhat.com/errata/RHSA-2026:60254
- https://access.redhat.com/errata/RHSA-2026:60252
- https://access.redhat.com/errata/RHSA-2026:60251
- https://access.redhat.com/errata/RHSA-2026:60250
- https://access.redhat.com/errata/RHSA-2026:60249
- https://access.redhat.com/errata/RHSA-2026:60248
- https://access.redhat.com/errata/RHSA-2026:60247
- https://access.redhat.com/errata/RHSA-2026:60246
- https://access.redhat.com/errata/RHSA-2026:60239
