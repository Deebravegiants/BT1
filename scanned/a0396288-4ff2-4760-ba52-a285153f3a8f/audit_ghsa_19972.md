# [H] markdown-it vulnerable to Inefficient Regular Expression Complexity

## Summary
Severity: High
Advisory: GHSA-j5p7-jf4q-742q
CVE: CVE-2015-10005
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-27
Source: https://github.com/advisories/GHSA-j5p7-jf4q-742q
Type: github-advisory

## Affected
- npm: `markdown-it` — affected >=0 <3.0.0

## Details
A vulnerability was found in markdown-it up to 2.x. It has been classified as problematic. Affected is an unknown function of the file `lib/common/html_re.js`. The manipulation leads to inefficient regular expression complexity. Upgrading to version 3.0.0 is able to address this issue. The name of the patch is 89c8620157d6e38f9872811620d25138fc9d1b0d. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-216852.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-10005
- https://github.com/markdown-it/markdown-it/commit/89c8620157d6e38f9872811620d25138fc9d1b0d
- https://github.com/markdown-it/markdown-it
- https://github.com/markdown-it/markdown-it/releases/tag/3.0.0
- https://vuldb.com/?ctiid.216852
- https://vuldb.com/?id.216852
