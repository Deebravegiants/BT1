# [H] kaml has potential denial of service while parsing input with anchors and aliases 

## Summary
Severity: High
Advisory: GHSA-c24f-2j3g-rg48
CVE: CVE-2023-28118
CWE: CWE-776
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-20
Source: https://github.com/advisories/GHSA-c24f-2j3g-rg48
Type: github-advisory

## Affected
- Maven: `com.charleskorn.kaml:kaml` — affected >=0 <0.53.0

## Details
### Impact
Applications that use kaml to parse untrusted input containing anchors and aliases may consume excessive memory and crash.

### Patches
Version 0.53.0 and later default to refusing to parse YAML documents containing anchors and aliases.

### Workarounds
None.

### References
Wikipedia has an explanation of this class of vulnerability: [billion laughs attack](https://en.wikipedia.org/wiki/Billion_laughs_attack)

### Acknowledgements
Thank you to @gdude2002 for reporting this issue.

## References
- https://github.com/charleskorn/kaml/security/advisories/GHSA-c24f-2j3g-rg48
- https://nvd.nist.gov/vuln/detail/CVE-2023-28118
- https://github.com/charleskorn/kaml/commit/5f82a2d7e00bfc307afca05d1dc4d7c50593531a
- https://github.com/charleskorn/kaml
- https://github.com/charleskorn/kaml/releases/tag/0.53.0
