# [M] Jenkins QMetry Test Management Plugin stores unencrypted API keys

## Summary
Severity: Medium
Advisory: GHSA-p9gh-rpjw-78qg
CVE: CVE-2025-53659
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-p9gh-rpjw-78qg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:qmetry-test-management` — affected >=0

## Details
QMetry Test Management Plugin 1.13 and earlier stores Qmetry Automation API Keys unencrypted in job `config.xml` files on the Jenkins controller as part of its configuration.

These API keys can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

Additionally, the job configuration form does not mask these API keys, increasing the potential for attackers to observe and capture them.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53659
- https://github.com/jenkinsci/qmetry-test-management-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3532
- http://www.openwall.com/lists/oss-security/2025/07/09/4
