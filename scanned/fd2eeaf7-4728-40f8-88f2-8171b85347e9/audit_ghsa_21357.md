# [C] easyii CMS's File Upload Management vulnerable to unrestricted upload

## Summary
Severity: Critical
Advisory: GHSA-vqvm-qrwh-69h7
CVE: CVE-2022-3771
CWE: CWE-284, CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-31
Source: https://github.com/advisories/GHSA-vqvm-qrwh-69h7
Type: github-advisory

## Affected
- Packagist: `noumo/easyii` — affected >=0

## Details
This issue affects the function file of the file helpers/Upload.php of the component File Upload Management. The manipulation leads to unrestricted upload. The attack may be initiated remotely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3771
- https://github.com/noumo/easyii
- https://vuldb.com/?id.212501
