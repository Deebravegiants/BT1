# [H] MAGMI plugin for Magento Unsafe File Upload

## Summary
Severity: High
Advisory: GHSA-x3gh-95p8-43qv
CVE: CVE-2014-8770
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-x3gh-95p8-43qv
Type: github-advisory

## Affected
- Packagist: `dweeves/magmi` — affected >=0

## Details
Unrestricted file upload vulnerability in `magmi/web/magmi.php` in the MAGMI (aka Magento Mass Importer) plugin 0.7.17a and earlier for Magento Community Edition (CE) allows remote authenticated users to execute arbitrary code by uploading a ZIP file that contains a PHP file, then accessing the PHP file via a direct request to it in `magmi/plugins/`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8770
- https://sourceforge.net/projects/magmi/files/magmi-0.7/plugins/packages
- http://www.exploit-db.com/exploits/35052
