# [M] AVideo through 29.0 Unauthenticated Disclosure via epg.json.php

## Summary
Severity: Medium
Advisory: CVE-2026-86728
Aliases: GHSA-xpr5-7246-qvh5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86728
Type: osv

## Details
AVideo through 29.0 contains an authentication bypass vulnerability in plugin/PlayLists/epg.json.php that exposes live-stream keys and private EPG schedules to unauthenticated users. Attackers can request the endpoint with sequential user or playlist IDs to retrieve sensitive credentials, server identifiers, and complete programme schedules without authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86728.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-xpr5-7246-qvh5
- https://nvd.nist.gov/vuln/detail/CVE-2026-86728
- https://www.vulncheck.com/advisories/avideo-through-29.0-unauthenticated-disclosure-via-epg-json-php
