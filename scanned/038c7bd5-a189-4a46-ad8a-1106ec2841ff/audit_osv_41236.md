# [M] Cockpit CMS 2.14.0 - Path Traversal Local File Inclusion via index.php

## Summary
Severity: Medium
Advisory: CVE-2026-58467
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-58467
Type: osv

## Details
Cockpit CMS through 2.14.0 contains a path traversal and local file inclusion vulnerability that allows unauthenticated attackers to read arbitrary files or execute PHP files by including unvalidated PATH_INFO derived from REQUEST_URI in filesystem path construction without containment checks. Attackers can inject dot-dot sequences into the URL to traverse outside the designated spaces directory, and when the resolved path ends with a .php extension, the application passes it to include(), enabling local file inclusion on deployments using the PHP built-in server or certain non-default Nginx configurations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58467.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58467
- https://www.vulncheck.com/advisories/cockpit-cms-path-traversal-local-file-inclusion-via-index-php
- https://github.com/cockpit-hq/cockpit
- https://github.com/geo-chen/oss/blob/main/cockpit.md
