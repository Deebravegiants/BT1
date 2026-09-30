# [H] Microweber allows Unrestricted File Upload

## Summary
Severity: High
Advisory: GHSA-89fp-j8v7-p82h
CVE: CVE-2020-13241
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-89fp-j8v7-p82h
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0

## Details
Microweber 1.1.18 allows Unrestricted File Upload because `admin/view:modules/load_module:users#edit-user=1` does not verify that the file extension (used with the Add Image option on the Edit User screen) corresponds to an image file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13241
- https://gist.github.com/virendratiwari03/0af29841fdf27207eb3abc8f28d326f3
- https://github.com/microweber/microweber
