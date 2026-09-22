# [C] Prototype Pollution in vConsole

## Summary
Severity: Critical
Advisory: GHSA-f737-3fh6-jf6w
CVE: CVE-2023-30363
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-f737-3fh6-jf6w
Type: github-advisory

## Affected
- npm: `vconsole` — affected >=0 <3.15.1

## Details
vConsole was discovered to contain a prototype pollution due to incorrect key and value resolution in setOptions in core.ts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30363
- https://github.com/Tencent/vConsole/issues/616
- https://github.com/Tencent/vConsole/commit/b91591703490e032451f7734212f6458bde9be6a
- https://cwe.mitre.org/data/definitions/1321.html
- https://github.com/Tencent/vConsole
- https://github.com/Tencent/vConsole/releases/tag/v3.15.1
