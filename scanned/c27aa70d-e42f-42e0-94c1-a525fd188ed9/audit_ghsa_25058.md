# [H] Stored XSS vulnerability in Jenkins Yet Another Build Visualizer Plugin

## Summary
Severity: High
Advisory: GHSA-3mwj-7vmq-w43p
CVE: CVE-2020-2236
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3mwj-7vmq-w43p
Type: github-advisory

## Affected
- Maven: `com.axis.system.jenkins.plugins.downstream:yet-another-build-visualizer` — affected >=0 <1.12

## Details
Yet Another Build Visualizer Plugin 1.11 and earlier does not escape tooltip content.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by users with Run/Update permission.

Yet Another Build Visualizer Plugin 1.12 escapes tooltip content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2236
- https://github.com/jenkinsci/yet-another-build-visualizer-plugin/commit/0e6db61ef66f4ed4f2e580240e364f195b00ee6e
- https://github.com/jenkinsci/yet-another-build-visualizer-plugin
- https://jenkins.io/security/advisory/2020-08-12/#SECURITY-1940
- http://www.openwall.com/lists/oss-security/2020/08/12/4
