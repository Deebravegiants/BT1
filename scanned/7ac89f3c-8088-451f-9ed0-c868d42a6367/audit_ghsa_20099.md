# [C] FurqanSoftware/node-whois vulnerable to Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-97jv-c342-5xhc
CVE: CVE-2020-36618
CWE: CWE-1321, CWE-74, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-19
Source: https://github.com/advisories/GHSA-97jv-c342-5xhc
Type: github-advisory

## Affected
- npm: `whois` — affected >=0 <2.13.6

## Details
A vulnerability classified as critical has been found in Furqan node-whois. Affected is an unknown function of the file `index.coffee`. The manipulation leads to improperly controlled modification of object prototype attributes ('prototype pollution'). It is possible to launch the attack remotely. The name of the patch is 46ccc2aee8d063c7b6b4dee2c2834113b7286076. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-216252.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36618
- https://github.com/FurqanSoftware/node-whois/pull/105
- https://github.com/FurqanSoftware/node-whois/commit/46ccc2aee8d063c7b6b4dee2c2834113b7286076
- https://github.com/FurqanSoftware/node-whois
- https://vuldb.com/?id.216252
- https://web.archive.org/web/20220403104013/https://www.npmjs.com/package/whois
