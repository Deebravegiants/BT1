# [M] Anki's local HTTP server is vulnerable to directory traversal attacks

## Summary
Severity: Medium
Advisory: CVE-2026-64677
Aliases: GHSA-78wr-2gg2-4hqg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-64677
Type: osv

## Details
Anki is a program for creating and reviewing flashcards. Prior to 25.09.3, endpoints in Anki's local HTTP server do not adequately constrain requested media and built-in data paths, allowing scripts served from shared decks, or malicious websites combined with an origin-check bypass, to read local files through directory traversal. This issue is fixed in version 25.09.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64677.json
- https://github.com/ankitects/anki/security/advisories/GHSA-78wr-2gg2-4hqg
- https://nvd.nist.gov/vuln/detail/CVE-2026-64677
- https://github.com/ankitects/anki/commit/f4692e54a4fafc89528afab1983f0b98d593023f
