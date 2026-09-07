# [M] Xataface vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-64wv-c7jw-jw2q
CVE: CVE-2021-4303
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-05
Source: https://github.com/advisories/GHSA-64wv-c7jw-jw2q
Type: github-advisory

## Affected
- Packagist: `xataface/xataface` — affected >=0 <3.0.0

## Details
A vulnerability, which was classified as problematic, has been found in shannah Xataface up to 2.x. Affected by this issue is the function testftp of the file install/install_form.js.php of the component Installer. The manipulation leads to cross site scripting. The attack may be launched remotely. Upgrading to version 3.0.0 can address this issue. The name of the patch is 94143a4299e386f33bf582139cd4702571d93bde. It is recommended to upgrade the affected component. VDB-217442 is the identifier assigned to this vulnerability. NOTE: Installer is disabled by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4303
- https://github.com/shannah/xataface/commit/94143a4299e386f33bf582139cd4702571d93bde
- https://github.com/shannah/xataface
- https://github.com/shannah/xataface/releases/tag/3.0.0
- https://vuldb.com/?ctiid.217442
- https://vuldb.com/?id.217442
