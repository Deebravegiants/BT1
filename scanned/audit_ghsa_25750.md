# [H] Server-side Template Injection in nystudio107/craft-seomatic

## Summary
Severity: High
Advisory: GHSA-m3xv-x3ph-mq22
CVE: CVE-2021-44618
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-m3xv-x3ph-mq22
Type: github-advisory

## Affected
- Packagist: `nystudio107/craft-seomatic` — affected >=0 <3.4.12

## Details
A Server-side Template Injection (SSTI) vulnerability exists in Nystudio107 Seomatic prior to 3.4.12 in src/helpers/UrlHelper.php via the host header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44618
- https://github.com/nystudio107/craft-seomatic/commit/0c5c0c0e0cb61000d12ec55ebf174745a5bf6469
- https://github.com/nystudio107/craft-seomatic
- https://github.com/nystudio107/craft-seomatic/releases/tag/3.4.12
