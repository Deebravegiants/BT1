# [C] Elefant CMS Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-77j2-7whr-6vpx
CVE: CVE-2018-16974
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-77j2-7whr-6vpx
Type: github-advisory

## Affected
- Packagist: `elefant/cms` — affected >=0 <2.0.7

## Details
An issue was discovered in Elefant CMS before 2.0.7. There is a PHP Code Execution Vulnerability in `apps/filemanager/upload/drop.php` by using `/filemanager/api/rm/.htaccess` to remove the .htaccess file, and then using a filename that ends in .php followed by space characters (for bypassing the blacklist).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16974
- https://github.com/jbroadway/elefant/issues/287
- https://github.com/jbroadway/elefant/commit/49ba8cc24e9f009ce30d2c2eb9eefeb9be4ce1d0
- https://github.com/jbroadway/elefant/releases/tag/elefant_2_0_7_stable
