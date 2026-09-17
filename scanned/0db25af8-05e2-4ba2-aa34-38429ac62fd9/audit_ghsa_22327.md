# [H] SEOmatic for CraftCMS allows Server-Side Template Injection

## Summary
Severity: High
Advisory: GHSA-23q7-59jj-2pj4
CVE: CVE-2020-12790
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-23q7-59jj-2pj4
Type: github-advisory

## Affected
- Packagist: `nystudio107/craft-seomatic` — affected >=0 <3.2.49

## Details
In the SEOmatic plugin before 3.2.49 for Craft CMS, helpers/DynamicMeta.php does not properly sanitize the URL. This leads to Server-Side Template Injection and credentials disclosure via a crafted Twig template after a semicolon.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12790
- https://github.com/nystudio107/craft-seomatic/commit/82f4a25b28fd622393da6592dc9e5ccee7fc5be3
- https://github.com/nystudio107/craft-seomatic/commit/82f4a25b28fd622393da6592dc9e5ccee7fc5be3#diff-52fd042c50432133a00a8f840f4a6165
- https://github.com/nystudio107/craft-seomatic
- https://github.com/nystudio107/craft-seomatic/blob/v3/CHANGELOG.md#3249---20200324
- https://github.com/nystudio107/craft-seomatic/releases/tag/3.2.49
- https://isec.pl/en/vulnerabilities/isec-0028-seomatic-ssti-23032020.txt
