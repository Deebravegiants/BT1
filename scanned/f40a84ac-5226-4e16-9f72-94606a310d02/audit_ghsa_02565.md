# [H] Arbitrary file upload in Fork CMS

## Summary
Severity: High
Advisory: GHSA-748f-wv76-x9hg
CVE: CVE-2021-28931
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-08
Source: https://github.com/advisories/GHSA-748f-wv76-x9hg
Type: github-advisory

## Affected
- Packagist: `forkcms/forkcms` — affected >=0 <5.9.3

## Details
Arbitrary file upload vulnerability in Fork CMS 5.9.2 allows attackers to create or replace arbitrary files in the /themes directory via a crafted zip file uploaded to the Themes panel.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28931
- https://github.com/forkcms/forkcms/pull/3351
- https://github.com/bousalman/ForkCMS-arbitrary-upload/blob/main/README.md
- https://github.com/forkcms/forkcms/releases/tag/5.9.2
