# [M] class.upload.php allows cross-site scripting attacks via uploaded files

## Summary
Severity: Medium
Advisory: GHSA-v6f4-jwv9-682w
CVE: CVE-2023-6551
CWE: CWE-20, CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-04
Source: https://github.com/advisories/GHSA-v6f4-jwv9-682w
Type: github-advisory

## Affected
- Packagist: `verot/class.upload.php` — affected >=0

## Details
As a simple library, class.upload.php does not perform an in-depth check on uploaded files, allowing a stored XSS vulnerability when the default configuration is used. 


Developers must be aware of that fact and use extension whitelisting accompanied by forcing the server to always provide content-type based on the file extension. 


The README has been updated to include these guidelines.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6551
- https://github.com/verot/class.upload.php/commit/befbccc2330b0ccb148fc87495896bd7b57f8c57
- https://cert.pl/en/posts/2024/01/CVE-2023-6551
- https://cert.pl/posts/2024/01/CVE-2023-6551
- https://github.com/verot/class.upload.php
