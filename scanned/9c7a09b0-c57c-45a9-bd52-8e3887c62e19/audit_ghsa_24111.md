# [M] Arbitrary file existence check in file fingerprints in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-f585-9fw3-rj2m
CVE: CVE-2021-21606
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f585-9fw3-rj2m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.263.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.264 <2.275

## Details
Jenkins provides a feature for jobs to store and track fingerprints of files used during a build. Jenkins 2.274 and earlier, LTS 2.263.1 and earlier provides a REST API to check where a given fingerprint was used by which builds. This endpoint does not fully validate that the provided fingerprint ID is properly formatted before checking for the XML metadata for that fingerprint on the controller file system.

This allows attackers with Overall/Read permission to check for the existence of XML files on the controller file system where the relative path can be constructed as 32 characters.

Jenkins 2.275, LTS 2.263.2 validates that a fingerprint ID is properly formatted before checking for its existence.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21606
- https://github.com/jenkinsci/jenkins/commit/f576b2eb4375f2bb076ce477cee27a946b65f22a
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-2023
