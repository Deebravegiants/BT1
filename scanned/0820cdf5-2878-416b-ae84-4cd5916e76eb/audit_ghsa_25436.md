# [H] Feehi CMS arbitrary file upload vulnerability

## Summary
Severity: High
Advisory: GHSA-65x8-9vgm-5fg5
CVE: CVE-2020-22643
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-65x8-9vgm-5fg5
Type: github-advisory

## Affected
- Packagist: `feehi/cms` — affected >=0

## Details
Feehi CMS 2.1.0-beta is affected by an arbitrary file upload vulnerability, potentially resulting in remote code execution. After an administrator logs in, open the administrator image upload page to potentially upload malicious files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-22643
- https://github.com/liufee/cms/issues/51
- https://github.com/liufee/cms
