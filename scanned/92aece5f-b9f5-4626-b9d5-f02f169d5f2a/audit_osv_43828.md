# [M] Grav before 2.0.15 Path Traversal via plugin-asset-map.php

## Summary
Severity: Medium
Advisory: CVE-2026-74907
Aliases: GHSA-4v9q-p283-qc2m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-74907
Type: osv

## Details
Grav before 2.0.15 contains a path traversal vulnerability in the static asset server within index.php that uses string prefix matching instead of directory-boundary validation. Unauthenticated attackers can access files in sibling directories by exploiting directory names that extend the base path string, such as requesting assets-secret when assets is the configured base.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74907.json
- https://github.com/getgrav/grav/security/advisories/GHSA-4v9q-p283-qc2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-74907
- https://www.vulncheck.com/advisories/grav-before-path-traversal-via-plugin-asset-map-php
