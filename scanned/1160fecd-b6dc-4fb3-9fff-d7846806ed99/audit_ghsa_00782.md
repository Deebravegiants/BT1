# [C] Remote code execution in verot/class.upload.php

## Summary
Severity: Critical
Advisory: GHSA-r5gm-4p5w-pq2p
CVE: CVE-2019-19576
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-01-16
Source: https://github.com/advisories/GHSA-r5gm-4p5w-pq2p
Type: github-advisory

## Affected
- Packagist: `verot/class.upload.php` — affected >=0 <1.0.3
- Packagist: `verot/class.upload.php` — affected >=2.0.0 <2.0.4

## Details
class.upload.php in verot.net class.upload before 1.0.3 and 2.x before 2.0.4, as used in the K2 extension for Joomla! and other products, omits .phar from the set of dangerous file extensions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19576
- https://github.com/getk2/k2/commit/d1344706c4b74c2ae7659b286b5a066117155124
- https://github.com/verot/class.upload.php/commit/5a7505ddec956fdc9e9c071ae5089865559174f1
- https://github.com/verot/class.upload.php/commit/db1b4fe50c1754696970d8b437f07e7b94a7ebf2
- https://github.com/jra89/CVE-2019-19576
- https://github.com/verot/class.upload.php/compare/1.0.2...1.0.3
- https://github.com/verot/class.upload.php/compare/2.0.3...2.0.4
- https://medium.com/%40jra8908/cve-2019-19576-e9da712b779
- https://medium.com/@jra8908/cve-2019-19576-e9da712b779
- https://www.verot.net
- https://www.verot.net/php_class_upload.htm
- http://packetstormsecurity.com/files/155577/Verot-2.0.3-Remote-Code-Execution.html
