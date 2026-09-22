# [H] Path Traversal in node-red-contrib-huemagic

## Summary
Severity: High
Advisory: GHSA-frpw-jrwx-hcfv
CVE: CVE-2021-25864
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-frpw-jrwx-hcfv
Type: github-advisory

## Affected
- npm: `node-red-contrib-huemagic` — affected >=0

## Details
node-red-contrib-huemagic 3.0.0 is affected by `hue/assets/..%2F` Directory Traversal.in the `res.sendFile` API, used in file hue-magic.js, to fetch an arbitrary file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25864
- https://github.com/Foddy/node-red-contrib-huemagic/issues/217
- https://github.com/Foddy/node-red-contrib-huemagic
