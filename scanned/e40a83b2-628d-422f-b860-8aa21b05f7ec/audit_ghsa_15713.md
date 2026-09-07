# [M] @aofl/cli-lib Prototype Pollution vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vg6v-jcg3-5mp7
CVE: CVE-2024-38987
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-vg6v-jcg3-5mp7
Type: github-advisory

## Affected
- npm: `@aofl/cli-lib` — affected >=0

## Details
aofl cli-lib v3.14.0 was discovered to contain a prototype pollution via the component defaultsDeep. This vulnerability allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38987
- https://github.com/AgeOfLearning/aofl/issues/35
- https://gist.github.com/mestrtee/29636943e6989e67f38251580cbcea73
- https://github.com/AgeOfLearning/aofl
