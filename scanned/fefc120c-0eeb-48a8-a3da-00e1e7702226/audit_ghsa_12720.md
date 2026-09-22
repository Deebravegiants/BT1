# [H] gry vulnerable to Command Injection

## Summary
Severity: High
Advisory: GHSA-w5mw-f2hq-5fw8
CVE: CVE-2020-36650
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-11
Source: https://github.com/advisories/GHSA-w5mw-f2hq-5fw8
Type: github-advisory

## Affected
- npm: `gry` — affected >=0 <6.0.0

## Details
A vulnerability, which was classified as critical, was found in IonicaBizau node-gry up to 5.x. This affects an unknown part. The manipulation leads to command injection. Upgrading to version 6.0.0 is able to address this issue. The name of the patch is 5108446c1e23960d65e8b973f1d9486f9f9dbd6c. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-218019.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36650
- https://github.com/IonicaBizau/node-gry/pull/22
- https://github.com/IonicaBizau/node-gry/commit/5108446c1e23960d65e8b973f1d9486f9f9dbd6c
- https://github.com/IonicaBizau/node-gry
- https://github.com/IonicaBizau/node-gry/releases/tag/6.0.0
- https://vuldb.com/?ctiid.218019
- https://vuldb.com/?id.218019
