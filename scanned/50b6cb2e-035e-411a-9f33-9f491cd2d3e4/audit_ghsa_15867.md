# [H] OS Command Injection in Snyk gradle plugin

## Summary
Severity: High
Advisory: GHSA-qqqw-gm93-qf6m
CVE: CVE-2024-48964
CWE: CWE-78, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-23
Source: https://github.com/advisories/GHSA-qqqw-gm93-qf6m
Type: github-advisory

## Affected
- npm: `snyk-gradle-plugin` — affected >=0 <4.5.0

## Details
The Snyk gradle plugin is vulnerable to Code Injection when scanning an untrusted Gradle project. The vulnerability can be triggered if Snyk test is run inside the untrusted project due to the improper handling of the current working directory name. Snyk recommends only scanning trusted projects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48964
- https://github.com/snyk/snyk-gradle-plugin/commit/2f5ee7579f00660282dd161a0b79690f4a9c865d
- https://github.com/snyk/snyk-gradle-plugin
