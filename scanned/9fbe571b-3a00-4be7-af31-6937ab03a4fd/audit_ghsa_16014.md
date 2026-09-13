# [H] OS Command Injection in Snyk php plugin

## Summary
Severity: High
Advisory: GHSA-69f9-h8f9-7vjf
CVE: CVE-2024-48963
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-23
Source: https://github.com/advisories/GHSA-69f9-h8f9-7vjf
Type: github-advisory

## Affected
- npm: `snyk-php-plugin` — affected >=0 <1.10.0

## Details
The Snyk php plugin is vulnerable to Code Injection when scanning an untrusted PHP project. The vulnerability can be triggered if Snyk test is run inside the untrusted project due to the improper handling of the current working directory name. Snyk recommends only scanning trusted projects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48963
- https://github.com/snyk/snyk-php-plugin/commit/9189f093b94f9ce51672f6919ffbc98171fd66d4
- https://github.com/snyk/snyk-php-plugin
- https://github.com/snyk/snyk-php-plugin/releases/tag/v1.10.0
