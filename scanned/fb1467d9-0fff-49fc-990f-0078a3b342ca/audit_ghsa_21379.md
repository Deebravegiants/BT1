# [M] Jenkins Compuware Topaz for Total Test Plugin allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-x5gv-5rqv-654m
CVE: CVE-2022-43427
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-x5gv-5rqv-654m
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-topaz-for-total-test` — affected >=0 <2.4.9

## Details
Jenkins Compuware Topaz for Total Test Plugin 2.4.8 and earlier does not perform permission checks in several HTTP endpoints, allowing attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43427
- https://github.com/jenkinsci/compuware-topaz-for-total-test-plugin/commit/0ba4274d545eac39e3db48b5dfb4512db3242946
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2623
- http://www.openwall.com/lists/oss-security/2022/10/19/3
