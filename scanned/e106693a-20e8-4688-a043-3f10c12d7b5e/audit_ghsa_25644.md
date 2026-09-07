# [H] Promotion names in Jenkins promoted builds Plugin are not validated when using Job DSL

## Summary
Severity: High
Advisory: GHSA-jmxr-w2jc-qp7w
CVE: CVE-2022-29049
CWE: CWE-20, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-jmxr-w2jc-qp7w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:promoted-builds` — affected >=0 <3.10.1
- Maven: `org.jenkins-ci.plugins:promoted-builds` — affected >=3.11 <876.v99d29788b

## Details
Jenkins promoted builds Plugin provides dedicated support for defining promotions using [Job DSL Plugin](https://plugins.jenkins.io/job-dsl).

promoted builds Plugin 873.v6149db_d64130 and earlier does not validate the names of promotions defined in Job DSL. This allows attackers with Job/Configure permission to create a promotion with an unsafe name. As a result, the promotion name could be used for cross-site scripting (XSS) or to replace other `config.xml` files.

promoted builds Plugin 876.v99d29788b_36b_ and 3.10.1 validates the name of promotions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29049
- https://github.com/jenkinsci/promoted-builds-plugin/commit/d6fd95688ae2052bf9ac7158bc2579c755167fe0
- https://github.com/jenkinsci/promoted-builds-plugin
- https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-2655
