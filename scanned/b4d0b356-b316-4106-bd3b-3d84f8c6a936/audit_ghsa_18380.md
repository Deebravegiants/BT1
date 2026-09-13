# [M] Jenkins Apica Loadtest Plugin vulnerability exposes authentication tokens

## Summary
Severity: Medium
Advisory: GHSA-q8p4-vw42-66gh
CVE: CVE-2025-53664
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-q8p4-vw42-66gh
Type: github-advisory

## Affected
- Maven: `com.apica:ApicaLoadtest` — affected >=0

## Details
Jenkins Apica Loadtest Plugin 1.10 and earlier stores Apica Loadtest LTP authentication tokens unencrypted in job `config.xml` files on the Jenkins controller as part of its configuration.

These tokens can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

Additionally, the job configuration form does not mask these tokens, increasing the potential for attackers to observe and capture them.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53664
- https://github.com/jenkinsci/apica-loadtest-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3540
- http://www.openwall.com/lists/oss-security/2025/07/09/4
