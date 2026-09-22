# [H] node-stringbuilder vulnerable to Out-of-bounds Read

## Summary
Severity: High
Advisory: GHSA-g533-xq5w-jmf3
CVE: CVE-2024-21524
CWE: CWE-125
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-g533-xq5w-jmf3
Type: github-advisory

## Affected
- npm: `node-stringbuilder` — affected >=0

## Details
All versions of the package node-stringbuilder are vulnerable to Out-of-bounds Read due to incorrect memory length calculation, by calling ToBuffer, ToString, or CharAt on a StringBuilder object with a non-empty string value input. It's possible to return previously allocated memory, for example, by providing negative indexes, leading to an Information Disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21524
- https://gist.github.com/dellalibera/0bb022811224f81d998fa61c3175ee67
- https://github.com/magiclen/node-stringbuilder
- https://github.com/magiclen/node-stringbuilder/blob/5c2797d3d6bf8cb6d10fe1e077609cef9a5a7de0/src/node-stringbuilder.c#L1281
- https://security.snyk.io/vuln/SNYK-JS-NODESTRINGBUILDER-6421617
