# [M] Audiobookshelf: Path prefix bypass in filesystem existence check leaks out-of-scope file existence

## Summary
Severity: Medium
Advisory: CVE-2026-42885
Aliases: GHSA-rhjg-p6cm-38w2
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-42885
Type: osv

## Details
Audiobookshelf is a self-hosted audiobook and podcast server. Prior to 2.32.2, the POST /api/filesystem/pathexists endpoint uses String.startsWith() to validate that a resolved file path is within a library folder. This check fails for sibling directories whose names share a common prefix (e.g., /audiobooks vs /audiobooks-private), allowing authenticated users with upload permission to probe file existence outside their authorized library folder boundaries. This vulnerability is fixed in 2.32.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42885.json
- https://github.com/advplyr/audiobookshelf/security/advisories/GHSA-rhjg-p6cm-38w2
- https://nvd.nist.gov/vuln/detail/CVE-2026-42885
