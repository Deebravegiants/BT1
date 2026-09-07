# [H] Jenkins Compuware Topaz for Total Test Plugin vulnerable to Protection Mechanism Failure

## Summary
Severity: High
Advisory: GHSA-7fvj-g3wp-29g8
CVE: CVE-2022-43429
CWE: CWE-284, CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-7fvj-g3wp-29g8
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-topaz-for-total-test` — affected >=0

## Details
Jenkins Compuware Topaz for Total Test Plugin 2.4.8 and earlier implements an agent/controller message that does not limit where it can be executed, allowing attackers able to control agent processes to read arbitrary files on the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43429
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2624
- http://www.openwall.com/lists/oss-security/2022/10/19/3
