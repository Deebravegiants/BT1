# [M] Jenkins Diagnostic page exposed session cookies

## Summary
Severity: Medium
Advisory: GHSA-4jjj-cm7q-v6hr
CVE: CVE-2020-2103
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4jjj-cm7q-v6hr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.205 <2.219
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.204.2

## Details
Jenkins shows various technical details about the current user on the `/whoAmI` page. In [a previous fix](https://www.jenkins.io/security/advisory/2019-09-25/#SECURITY-1505), the `Cookie` header value containing the HTTP session ID was redacted. However, user metadata shown on this page could also include the HTTP session ID in Jenkins 2.218 and earlier, LTS 2.204.1 and earlier.

This allows attackers able to exploit a cross-site scripting vulnerability to obtain the HTTP session ID value from this page.

Jenkins 2.219, LTS 2.204.2 no longer prints out the affected user metadata that might contain the HTTP session ID.

Additionally, we also redact values of further authentication-related HTTP headers in addition to `Cookie` on this page as a hardening.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2103
- https://github.com/jenkinsci/jenkins/commit/77f36f37f5e3cabd0e4ece16d46d7943454ed15b
- https://access.redhat.com/errata/RHBA-2020:0402
- https://access.redhat.com/errata/RHBA-2020:0675
- https://access.redhat.com/errata/RHSA-2020:0681
- https://access.redhat.com/errata/RHSA-2020:0683
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2020-01-29/#SECURITY-1695
- http://www.openwall.com/lists/oss-security/2020/01/29/1
