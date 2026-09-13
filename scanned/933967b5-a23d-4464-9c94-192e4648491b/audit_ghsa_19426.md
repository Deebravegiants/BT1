# [M] Jenkins Cadence vManager Plugin Stores Verisium Manager vAPI keys Unencrypted

## Summary
Severity: Medium
Advisory: GHSA-x9hj-q7xv-fv4v
CVE: CVE-2025-31724
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-02
Source: https://github.com/advisories/GHSA-x9hj-q7xv-fv4v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vmanager-plugin` — affected >=0 <4.0.1

## Details
Jenkins Cadence vManager Plugin 4.0.0-282.v5096a_c2db_275 and earlier stores Verisium Manager vAPI keys unencrypted in job `config.xml` files on the Jenkins controller as part of its configuration.

These API keys can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

Cadence vManager Plugin 4.0.1-286.v9e25a_740b_a_48 stores Verisium Manager vAPI keys encrypted once affected job configurations are saved again.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-31724
- https://github.com/jenkinsci/vmanager-plugin/commit/9e25a740ba4837ef528c73b621259e840ef0db75
- https://github.com/jenkinsci/vmanager-plugin
- https://www.jenkins.io/security/advisory/2025-04-02/#SECURITY-3537
