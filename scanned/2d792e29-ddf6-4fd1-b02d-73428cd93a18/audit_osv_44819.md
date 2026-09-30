# [M] AVideo through 29.0 Information Disclosure via restreamsActive.json.php

## Summary
Severity: Medium
Advisory: CVE-2026-86726
Aliases: GHSA-qh45-c3p8-jh4g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86726
Type: osv

## Details
AVideo through 29.0 contains an information disclosure vulnerability in restreamsActive.json.php that allows authenticated streamers to enumerate source stream keys and identities of all other streamers' active restreams. The endpoint fails to filter results by user ownership, exposing sensitive transmission credentials and streamer identity across all accounts to any user with streaming capability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86726.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-qh45-c3p8-jh4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-86726
- https://www.vulncheck.com/advisories/avideo-through-29.0-information-disclosure-via-restreamsactive-json-php
