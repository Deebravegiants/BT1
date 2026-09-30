# [H] Unrestricted Upload of File with Dangerous Type in WPanel 4

## Summary
Severity: High
Advisory: GHSA-vhgr-gfx3-fg37
CVE: CVE-2021-34257
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-01
Source: https://github.com/advisories/GHSA-vhgr-gfx3-fg37
Type: github-advisory

## Affected
- Packagist: `wpanel/wpanel4-cms` — affected >=0

## Details
Multiple Remote Code Execution (RCE) vulnerabilities exist in WPanel 4 4.3.1 and below via a malicious PHP file upload to (1) Dashboard's Avatar image, (2) Posts Folder image, (3) Pages Folder image and (4) Gallery Folder image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34257
- https://github.com/Sentinal920/WPanel4-Authenticated-RCE
- https://github.com/wpanel/wpanel4-cms
- https://latestpcsolution.wordpress.com/2021/06/05/wpanel4-cms-authenticated-rce
