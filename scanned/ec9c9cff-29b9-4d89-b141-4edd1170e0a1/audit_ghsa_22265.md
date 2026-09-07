# [M] CSRF vulnerabilities in Jenkins requests-plugin Plugin

## Summary
Severity: Medium
Advisory: GHSA-5frh-wx6v-8m2r
CVE: CVE-2021-21675
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5frh-wx6v-8m2r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:requests` — affected >=0 <2.2.13

## Details
Jenkins requests-plugin Plugin 2.2.12 and earlier does not require POST requests to request and apply changes, resulting in cross-site request forgery (CSRF) vulnerabilities.

These vulnerabilities allow attackers to create requests and/or have administrators apply pending requests, like renaming or deleting jobs, deleting builds, etc.

Jenkins requests-plugin Plugin 2.2.13 requires POST requests for the affected HTTP endpoints. This was partially fixed in requests-plugin Plugin 2.2.8 to require POST requests for some of the affected HTTP endpoints, but the endpoint allowing administrators to apply pending requests remained unprotected until 2.2.13.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21675
- https://github.com/jenkinsci/requests-plugin
- https://www.jenkins.io/security/advisory/2021-06-30/#SECURITY-2136%20(1)
- http://www.openwall.com/lists/oss-security/2021/06/30/1
