# [H] skeemas Inefficient Regular Expression Complexity vulnerability

## Summary
Severity: High
Advisory: GHSA-qv66-f876-vjvr
CVE: CVE-2018-25074
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-11
Source: https://github.com/advisories/GHSA-qv66-f876-vjvr
Type: github-advisory

## Affected
- npm: `skeemas` — affected >=0 <1.2.5

## Details
A vulnerability was found in Prestaul skeemas and classified as problematic. This issue affects some unknown processing of the file validators/base.js. The manipulation of the argument uri leads to inefficient regular expression complexity. The name of the patch is 65e94eda62dc8dc148ab3e59aa2ccc086ac448fd. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-218003.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25074
- https://github.com/Prestaul/skeemas/commit/65e94eda62dc8dc148ab3e59aa2ccc086ac448fd
- https://github.com/Prestaul/skeemas
- https://vuldb.com/?ctiid.218003
- https://vuldb.com/?id.218003
