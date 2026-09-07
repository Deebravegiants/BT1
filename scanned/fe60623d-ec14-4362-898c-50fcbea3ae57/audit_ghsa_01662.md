# [C] class.upload.php in verot.net omits .pht from the set of dangerous file extensions

## Summary
Severity: Critical
Advisory: GHSA-2gc7-w4hw-rr2m
CVE: CVE-2019-19634
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-28
Source: https://github.com/advisories/GHSA-2gc7-w4hw-rr2m
Type: github-advisory

## Affected
- Packagist: `verot/class.upload.php` — affected >=0
- Packagist: `verot/class.upload.php` — affected >=2.0.0

## Details
class.upload.php in verot.net class.upload through 1.0.3 and 2.x through 2.0.4, as used in the K2 extension for Joomla! and other products, omits .pht from the set of dangerous file extensions, a similar issue to CVE-2019-19576.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19634
- https://github.com/jra89/CVE-2019-19634
- https://github.com/verot/class.upload.php/blob/2.0.4/src/class.upload.php#L3068
- https://medium.com/%40jra8908/cve-2019-19634-arbitrary-file-upload-in-class-upload-php-ccaf9e13875e
- https://medium.com/@jra8908/cve-2019-19634-arbitrary-file-upload-in-class-upload-php-ccaf9e13875e
