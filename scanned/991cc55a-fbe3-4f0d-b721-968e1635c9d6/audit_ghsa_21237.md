# [M] Jenkins Files Found Trigger Plugin allows attackers to check for existence of attacker-specified file path on Jenkins controller file system

## Summary
Severity: Medium
Advisory: GHSA-jj8j-6jq7-gmvh
CVE: CVE-2022-36914
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-jj8j-6jq7-gmvh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:files-found-trigger` — affected >=0

## Details
Jenkins Files Found Trigger Plugin 1.5 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to check for the existence of an attacker-specified file path on the Jenkins controller file system. A sequence of requests can be used to effectively list the Jenkins controller file system.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36914
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2210
- http://www.openwall.com/lists/oss-security/2022/07/27/1
