# [H] Jenkins arbitrary type deserialization from attacker-controlled config.xml allows remote code execution and user impersonation

## Summary
Severity: High
Advisory: GHSA-g2xq-2v27-4rh3
CVE: CVE-2026-53435
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-g2xq-2v27-4rh3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.555.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.556 <2.568

## Details
In Jenkins 2.567 and earlier, LTS 2.555.2 and earlier, it is possible for attackers to have Jenkins deserialize arbitrary types defined in Jenkins core or plugins from an attacker-controlled `config.xml` submission in a way that allows them to handle HTTP requests afterwards.

This can be used to impersonate any user and send HTTP requests on their behalf, up to and including use of the Script Console to run arbitrary code, or to read arbitrary files from the Jenkins controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53435
- https://github.com/jenkinsci/jenkins/commit/d739f6a6266d
- https://github.com/jenkinsci/jenkins/commit/345a3190a49d1ac96c4ff1c2e9eef4102c8d63f6
- https://www.jenkins.io/security/advisory/2026-06-10/#SECURITY-3707
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53435.json
- https://github.com/jenkinsci/jenkins
- https://bugzilla.redhat.com/show_bug.cgi?id=2487539
- https://access.redhat.com/security/cve/CVE-2026-53435
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
