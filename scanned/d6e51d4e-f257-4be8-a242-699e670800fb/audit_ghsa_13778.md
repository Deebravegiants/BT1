# [C] openssl npm package vulnerable to command execution

## Summary
Severity: Critical
Advisory: GHSA-75w2-qv55-x7fv
CVE: CVE-2023-49210
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-23
Source: https://github.com/advisories/GHSA-75w2-qv55-x7fv
Type: github-advisory

## Affected
- npm: `openssl` — affected >=0

## Details
The openssl (aka node-openssl) NPM package through 2.0.0 was characterized as "a nonsense wrapper with no real purpose" by its author, and accepts an opts argument that contains a verb field (used for command execution). NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49210
- https://gist.github.com/mcoimbra/b05a55a5760172dccaa0a827647ad63e
- https://github.com/ossf/malicious-packages/tree/main/malicious/npm
- https://www.npmjs.com/package/openssl
