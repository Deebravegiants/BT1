# [H] AList vulnerable to Improper Preservation of Permissions

## Summary
Severity: High
Advisory: GHSA-4gjr-vgfx-9qvw
CVE: CVE-2022-45968
CWE: CWE-281, CWE-434
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-4gjr-vgfx-9qvw
Type: github-advisory

## Affected
- Go: `github.com/alist-org/alist/v3` — affected >=0 <3.5.1

## Details
Alist v3.4.0 is vulnerable to File Upload. A user with only file upload permission can upload any file to any folder (even a password protected one). Version 3.5.1 contains a patch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45968
- https://github.com/alist-org/alist/issues/2444
- https://github.com/alist-org/alist/commit/85e1350af82e1759ca6580895e48ab969eb566cf
- https://github.com/alist-org/alist
