# [M] Jenkins monitor-remote-job Plugin Stores Passwords Unencrypted

## Summary
Severity: Medium
Advisory: GHSA-g65g-fmcp-4w68
CVE: CVE-2025-31725
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-02
Source: https://github.com/advisories/GHSA-g65g-fmcp-4w68
Type: github-advisory

## Affected
- Maven: `org.ukiuni.monitor-remote-job-plugin:monitor-remote-job` — affected 1.0

## Details
Jenkins monitor-remote-job Plugin 1.0 stores passwords unencrypted in job `config.xml` files on the Jenkins controller as part of its configuration.

These passwords can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-31725
- https://github.com/jenkinsci/monitor-remote-job-plugin
- https://www.jenkins.io/security/advisory/2025-04-02/#SECURITY-3539
