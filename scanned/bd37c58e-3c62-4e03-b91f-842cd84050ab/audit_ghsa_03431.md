# [M] Improper Control of Dynamically-Managed Code Resources in config-shield

## Summary
Severity: Medium
Advisory: GHSA-w8h4-vw8f-rvvj
CVE: CVE-2021-26276
CWE: CWE-913
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-w8h4-vw8f-rvvj
Type: github-advisory

## Affected
- npm: `config-shield` — affected >=0 <0.2.3

## Details
scripts/cli.js in the GoDaddy node-config-shield (aka Config Shield) package before 0.2.2 for Node.js calls eval when processing a set command. **NOTE:** the vendor reportedly states that this is not a vulnerability. The set command was not intended for use with untrusted data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26276
- https://github.com/godaddy/node-config-shield/commit/cdba5d3a7accd661ffbc52e208153464bd0d9da6
- https://advisory.checkmarx.net/advisory/CX-2021-4773
- https://github.com/godaddy/node-config-shield
