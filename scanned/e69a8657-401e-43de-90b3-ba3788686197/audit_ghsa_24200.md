# [M] Reflected XSS vulnerability in Jenkins markup formatter preview

## Summary
Severity: Medium
Advisory: GHSA-7qf3-c2q8-69m3
CVE: CVE-2021-21610
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7qf3-c2q8-69m3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.263.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.264 <2.275

## Details
Jenkins allows administrators to choose the markup formatter to use for descriptions of jobs, builds, views, etc. displayed in Jenkins. When editing such a description, users can choose to have Jenkins render a formatted preview of the description they entered.

Jenkins 2.274 and earlier, LTS 2.263.1 and earlier does not implement any restrictions for the URL rendering the formatted preview of markup passed as a query parameter. This results in a reflected cross-site scripting (XSS) vulnerability if the configured markup formatter does not prohibit unsafe elements (JavaScript) in markup, like [Anything Goes Formatter Plugin](https://plugins.jenkins.io/anything-goes-formatter/).

Jenkins 2.275, LTS 2.263.2 requires that preview URLs are accessed using POST and sets Content-Security-Policy headers that prevent execution of unsafe elements when the URL is accessed directly.

In case of problems with this change, these protections can be disabled by setting the [Java system properties](https://www.jenkins.io/doc/book/managing/system-properties/) `hudson.markup.MarkupFormatter.previewsAllowGET` to `true` and/or `hudson.markup.MarkupFormatter.previewsSetCSP` to `false`. Doing either is discouraged.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21610
- https://github.com/jenkinsci/jenkins/commit/89ec0c40b68cd1e4e9f9ef5ebcafd87e7fa16589
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-2153
