# [H] Code Injection in pac-resolver

## Summary
Severity: High
Advisory: GHSA-9j49-mfvp-vmhm
CVE: CVE-2021-23406
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-9j49-mfvp-vmhm
Type: github-advisory

## Affected
- npm: `pac-resolver` — affected >=0 <5.0.0
- npm: `degenerator` — affected >=0 <3.0.1

## Details
This affects the package pac-resolver before 5.0.0. This can occur when used with untrusted input, due to unsafe PAC file handling. **NOTE:** The fix for this vulnerability is applied in the node-degenerator library, a dependency written by the same maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23406
- https://github.com/TooTallNate/node-degenerator/commit/9d25bb67d957bc2e5425fea7bf7a58b3fc64ff9e
- https://github.com/TooTallNate/node-degenerator/commit/ccc3445354135398b6eb1a04c7d27c13b833f2d5
- https://github.com/TooTallNate
- https://github.com/TooTallNate/node-pac-resolver/releases/tag/5.0.0
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1568506
- https://snyk.io/vuln/SNYK-JS-PACRESOLVER-1564857
