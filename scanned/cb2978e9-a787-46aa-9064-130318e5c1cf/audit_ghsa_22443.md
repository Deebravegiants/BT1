# [M] Incorrect permission check in Health Advisor by CloudBees Plugin

## Summary
Severity: Medium
Advisory: GHSA-c445-xm3f-hmfh
CVE: CVE-2020-2258
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c445-xm3f-hmfh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cloudbees-jenkins-advisor` — affected >=0 <3.2.1

## Details
Health Advisor by CloudBees Plugin 3.2.0 and earlier does not correctly perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to view an administrative configuration page.

Health Advisor by CloudBees Plugin 3.2.1 requires Overall/Administer to view its administrative configuration page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2258
- https://github.com/jenkinsci/cloudbees-jenkins-advisor-plugin/commit/90f693a4b9fc60292463ecd7aa06c2c53d9dea30
- https://github.com/jenkinsci/cloudbees-jenkins-advisor-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1998
- http://www.openwall.com/lists/oss-security/2020/09/16/3
