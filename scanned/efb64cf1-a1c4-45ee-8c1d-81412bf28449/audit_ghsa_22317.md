# [M] View name validation bypass in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-w2hv-rcqr-2h7r
CVE: CVE-2021-21640
CWE: CWE-240
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w2hv-rcqr-2h7r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.277.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.278 <2.287

## Details
Jenkins 2.286 and earlier, LTS 2.277.1 and earlier does not properly check that a newly created view has an allowed name. When a form to create a view is submitted, the name is included twice in the submission. One instance is validated, but the other instance is used to create the value.

This allows attackers with View/Create permission to create views with invalid or already-used names.

Jenkins 2.287, LTS 2.277.2 uses the same submitted value for validation and view creation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21640
- https://github.com/jenkinsci/jenkins/commit/42e2c74049ddf5e0aca1fe6aadc7b24fdabb5494
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-04-07/#SECURITY-1871
- http://www.openwall.com/lists/oss-security/2021/04/07/2
