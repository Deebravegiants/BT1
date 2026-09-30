# [C] Prototype pollution in nconf-toml

## Summary
Severity: Critical
Advisory: GHSA-hx7j-43w2-7rj7
CVE: CVE-2021-25946
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-07
Source: https://github.com/advisories/GHSA-hx7j-43w2-7rj7
Type: github-advisory

## Affected
- npm: `nconf-toml` — affected >=0.0.1

## Details
Prototype pollution vulnerability in `nconf-toml` versions 0.0.1 through 0.0.2 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25946
- https://github.com/RobLoach/nconf-toml
- https://github.com/RobLoach/nconf-toml/blob/8ade08cd1cfb9691ab7cc5c3514cc05c5085918f/index.js#L8
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25946
