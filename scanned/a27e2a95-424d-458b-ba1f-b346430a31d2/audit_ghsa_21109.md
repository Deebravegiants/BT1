# [M] Jenkins Android Signing Plugin allows attackers to check whether attacker-specified file patterns match workspace contents

## Summary
Severity: Medium
Advisory: GHSA-vp68-fm96-7v79
CVE: CVE-2022-36915
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-vp68-fm96-7v79
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:android-signing` — affected >=0

## Details
Jenkins Android Signing Plugin 2.2.5 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Item/Read permission but without Item/Workspace or Item/Configure permission to check whether attacker-specified file patterns match workspace contents. A sequence of requests can be used to effectively list workspace contents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36915
- https://github.com/jenkinsci/android-signing-plugin/commit/33162c65c9f52ca5fa85609bdb652a5d1feda95b
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2404
- http://www.openwall.com/lists/oss-security/2022/07/27/1
