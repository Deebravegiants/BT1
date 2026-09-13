# [M] OpenDeck affected by path traversal allows arbitrary file read

## Summary
Severity: Medium
Advisory: CVE-2026-28427
Aliases: GHSA-4974-g27q-h5m8
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:L/SI:L/SA:L)
Published: 2026-03-04
Source: https://osv.dev/vulnerability/CVE-2026-28427
Type: osv

## Details
OpenDeck is Linux software for your Elgato Stream Deck. Prior to 2.8.1, the service listening on port 57118 serves static files for installed plugins but does not properly sanitize path components. By including ../ sequences in the request path, an attacker can traverse outside the intended directory and read any file OpenDeck can access. This vulnerability is fixed in 2.8.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28427.json
- https://github.com/nekename/OpenDeck/security/advisories/GHSA-4974-g27q-h5m8
- https://nvd.nist.gov/vuln/detail/CVE-2026-28427
- https://github.com/nekename/OpenDeck/commit/488a52050017e95a72ba448226ac5e19a20dd9ed
