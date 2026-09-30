# [M] Missing Authorization in Jenkins Pipeline: Shared Groovy Libraries Plugin

## Summary
Severity: Medium
Advisory: GHSA-9x5v-8352-244g
CVE: CVE-2019-10357
CWE: CWE-285, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9x5v-8352-244g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-cps-global-lib` — affected >=0 <2.15

## Details
A missing permission check in Jenkins Pipeline: Shared Groovy Libraries Plugin 2.14 and earlier allowed users with Overall/Read access to obtain limited information about the content of SCM repositories referenced by global libraries.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10357
- https://github.com/jenkinsci/workflow-cps-global-lib-plugin/commit/6fce1e241d82641e8648c546bc63c22a5e07e96b
- https://access.redhat.com/errata/RHSA-2019:2594
- https://access.redhat.com/errata/RHSA-2019:2651
- https://access.redhat.com/errata/RHSA-2019:2662
- https://github.com/jenkinsci/workflow-cps-global-lib-plugin
- https://jenkins.io/security/advisory/2019-07-31/#SECURITY1422
- http://www.openwall.com/lists/oss-security/2019/07/31/1
