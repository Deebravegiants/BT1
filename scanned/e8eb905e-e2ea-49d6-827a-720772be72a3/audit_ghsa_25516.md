# [C] Command injection in npm-dependency-versions

## Summary
Severity: Critical
Advisory: GHSA-m7xq-8jp8-rj2c
CVE: CVE-2022-29080
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-m7xq-8jp8-rj2c
Type: github-advisory

## Affected
- npm: `npm-dependency-versions` — affected >=0

## Details
The npm-dependency-versions package through 0.3.0 for Node.js allows command injection if an attacker is able to call dependencyVersions with a JSON object in which pkgs is a key, and there are shell metacharacters in a value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29080
- https://github.com/barneycarroll/npm-dependency-versions/issues/6
- https://github.com/barneycarroll/npm-dependency-versions
- https://www.npmjs.com/package/npm-dependency-versions
