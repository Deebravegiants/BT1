# [M] Jenkins Port Allocator Plugin stores credentials in plain text

## Summary
Severity: Medium
Advisory: GHSA-5hhg-q22c-6g39
CVE: CVE-2019-10350
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5hhg-q22c-6g39
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:port-allocator` — affected >=0

## Details
Jenkins Port Allocator Plugin stores credentials unencrypted in job `config.xml` files on the Jenkins controller. These credentials can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10350
- https://jenkins.io/security/advisory/2019-07-11/#SECURITY-1441
- http://www.openwall.com/lists/oss-security/2019/07/11/4
