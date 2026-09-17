# [M] Missing permission check in Jenkins CloudBees CD Plugin allows scheduling builds

## Summary
Severity: Medium
Advisory: GHSA-7rx6-4vwv-432g
CVE: CVE-2021-21647
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7rx6-4vwv-432g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:electricflow` — affected >=0 <1.1.18.1
- Maven: `org.jenkins-ci.plugins:electricflow` — affected >=1.1.19 <1.1.22

## Details
Jenkins CloudBees CD Plugin does not perform a permission check in an HTTP endpoint.

This allows attackers with Item/Read permission to schedule builds of projects without having Item/Build permission.

Jenkins CloudBees CD Plugin requires Item/Build permission to schedule builds via its HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21647
- https://github.com/jenkinsci/electricflow-plugin/commit/597cbb1d767ae92c44b4cbd9525fa53ddab37117
- https://github.com/jenkinsci/electricflow-plugin
- https://www.jenkins.io/security/advisory/2021-04-21/#SECURITY-2309
- http://www.openwall.com/lists/oss-security/2021/04/21/2
