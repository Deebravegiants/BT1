# [M] Audiobookshelf: Collection endpoints bypass library access controls exposing restricted library data

## Summary
Severity: Medium
Advisory: CVE-2026-42884
Aliases: GHSA-rxw2-h55w-ffmh
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-42884
Type: osv

## Details
Audiobookshelf is a self-hosted audiobook and podcast server. Prior to 2.32.2, the GET /api/collections and GET /api/collections/:id endpoints return collections from all libraries without checking whether the requesting user has access to each collection's library. An authenticated user with access to any library can enumerate and read collections (including full book metadata) from libraries they are explicitly restricted from accessing. This vulnerability is fixed in 2.32.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42884.json
- https://github.com/advplyr/audiobookshelf/security/advisories/GHSA-rxw2-h55w-ffmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-42884
