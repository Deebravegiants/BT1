# [H] Incorrect Privilege Assignment in Jenkins Script Security Plugin

## Summary
Severity: High
Advisory: GHSA-p56j-x44h-g66j
CVE: CVE-2019-10355
CWE: CWE-266, CWE-704
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p56j-x44h-g66j
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1.62

## Details
A sandbox bypass vulnerability in Jenkins Script Security Plugin 1.61 and earlier related to the handling of type casts allowed attackers to execute arbitrary code in sandboxed scripts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10355
- https://github.com/jenkinsci/script-security-plugin/commit/5dc2e2465f309c772237a4b2de9caf61ba9b585b
- https://access.redhat.com/errata/RHSA-2019:2594
- https://access.redhat.com/errata/RHSA-2019:2651
- https://access.redhat.com/errata/RHSA-2019:2662
- https://github.com/jenkinsci/script-security-plugin
- https://jenkins.io/security/advisory/2019-07-31/#SECURITY-1465
- http://www.openwall.com/lists/oss-security/2019/07/31/1
