# [M] AVideo through 29.0 Information Disclosure via stats.json.php

## Summary
Severity: Medium
Advisory: CVE-2026-86727
Aliases: GHSA-8g4j-g3r6-73xr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86727
Type: osv

## Details
AVideo through 29.0 contains an information disclosure vulnerability in plugin/Live/stats.json.php that allows unauthenticated attackers to retrieve stream keys and m3u8 URLs by accessing the endpoint without authentication. Attackers can enumerate private, unlisted, and group-restricted live streams by parsing the hidden_applications array in the JSON response to obtain sensitive streaming credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86727.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-8g4j-g3r6-73xr
- https://nvd.nist.gov/vuln/detail/CVE-2026-86727
- https://www.vulncheck.com/advisories/avideo-through-29.0-information-disclosure-via-stats-json-php
