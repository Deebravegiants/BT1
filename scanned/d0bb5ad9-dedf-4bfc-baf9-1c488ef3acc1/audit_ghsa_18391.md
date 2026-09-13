# [M] Jenkins Statistics Gatherer Plugin vulnerability exposes AWS Secret Key

## Summary
Severity: Medium
Advisory: GHSA-3c9f-c64m-h4wc
CVE: CVE-2025-53654
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-3c9f-c64m-h4wc
Type: github-advisory

## Affected
- Maven: `org.jenkins.plugins.statistics.gatherer:statistics-gatherer` — affected >=0

## Details
Jenkins Statistics Gatherer Plugin 2.0.3 and earlier stores the AWS Secret Key unencrypted in its global configuration file `org.jenkins.plugins.statistics.gatherer.StatisticsConfiguration.xml` on the Jenkins controller as part of its configuration.

This key can be viewed by users with access to the Jenkins controller file system.

Additionally, the global configuration form does not mask this key, increasing the potential for attackers to observe and capture it.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53654
- https://github.com/jenkinsci/statistics-gatherer-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3554
- http://www.openwall.com/lists/oss-security/2025/07/09/4
