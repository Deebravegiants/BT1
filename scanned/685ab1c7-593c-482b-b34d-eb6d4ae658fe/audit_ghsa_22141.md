# [M] Jenkins Azure Event Grid Build Notifier Plugin has Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-826h-fxff-hpqf
CVE: CVE-2019-10421
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-826h-fxff-hpqf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:azure-event-grid-notifier` — affected >=0

## Details
Azure Event Grid Build Notifier Plugin stores the Azure Event Grid secret key unencrypted in job `config.xml` files on the Jenkins controller. This key can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10421
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-1544
- http://www.openwall.com/lists/oss-security/2019/09/25/3
