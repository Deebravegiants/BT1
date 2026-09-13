# [M] Jenkins exposes other users' timezone and view names to users with Overall/Read permission

## Summary
Severity: Medium
Advisory: GHSA-g28p-6mcc-v4rv
CVE: CVE-2026-53439
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-g28p-6mcc-v4rv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.555.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.556 <2.568

## Details
Missing permission checks in Jenkins 2.567 and earlier, LTS 2.555.2 and earlier allow attackers with Overall/Read permission to determine other users' configured timezone and to enumerate view names of other users' "My Views".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53439
- https://github.com/jenkinsci/jenkins/commit/0586de425598497cfb4dcdafa5007e507a440a77
- https://github.com/jenkinsci/jenkins/commit/98fe05f1753f664ffddd295a03492684b74e1950
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2026-06-10/#SECURITY-3713
