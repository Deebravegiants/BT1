# [H] rgb2hex vulnerable to inefficient regular expression complexity

## Summary
Severity: High
Advisory: GHSA-7599-fqgm-v84p
CVE: CVE-2018-25061
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-31
Source: https://github.com/advisories/GHSA-7599-fqgm-v84p
Type: github-advisory

## Affected
- npm: `rgb2hex` — affected >=0 <0.1.6

## Details
A vulnerability was found in rgb2hex up to 0.1.5. It has been rated as problematic. This issue affects some unknown processing. The manipulation leads to inefficient regular expression complexity. The attack may be initiated remotely. Upgrading to version 0.1.6 can address this issue. The name of the patch is 9e0c38594432edfa64136fdf7bb651835e17c34f. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-217151.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25061
- https://github.com/christian-bromann/rgb2hex/commit/9e0c38594432edfa64136fdf7bb651835e17c34f
- https://github.com/christian-bromann/rgb2hex
- https://github.com/christian-bromann/rgb2hex/releases/tag/v0.1.6
- https://vuldb.com/?ctiid.217151
- https://vuldb.com/?id.217151
