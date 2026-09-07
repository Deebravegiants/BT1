# [M] Jenkins IFTTT Build Notifier Plugin vulnerability exposes IFTTT Maker Channel Keys

## Summary
Severity: Medium
Advisory: GHSA-jxwj-qccf-4896
CVE: CVE-2025-53662
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-jxwj-qccf-4896
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ifttt-build-notifier` — affected >=0

## Details
Jenkins IFTTT Build Notifier Plugin 1.2 and earlier stores IFTTT Maker Channel Keys unencrypted in job `config.xml` files on the Jenkins controller as part of its configuration.

These keys can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53662
- https://github.com/jenkinsci/ifttt-build-notifier-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3541
- http://www.openwall.com/lists/oss-security/2025/07/09/4
