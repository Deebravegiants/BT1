# [H] FrozenNode Laravel-Administrator unrestricted file upload

## Summary
Severity: High
Advisory: GHSA-9r2j-rg24-fvpj
CVE: CVE-2020-10963
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9r2j-rg24-fvpj
Type: github-advisory

## Affected
- Packagist: `frozennode/administrator` — affected >=0

## Details
FrozenNode Laravel-Administrator through 5.0.12 allows unrestricted file upload (and consequently Remote Code Execution) via `admin/tips_image/image/file_upload` image upload with PHP content within a GIF image that has the `.php` extension. NOTE: this product is discontinued.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10963
- https://xavibel.com/2020/03/23/unrestricted-file-upload-in-frozennode-laravel-administrator
- http://packetstormsecurity.com/files/160243/Laravel-Administrator-4-File-Upload.html
