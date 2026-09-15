# [M] Docmost's Public Share Search Exposes Metadata of Restricted Children

## Summary
Severity: Medium
Advisory: CVE-2026-33146
Aliases: GHSA-qq4c-8rjr-w42c
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-33146
Type: osv

## Details
Docmost is open-source collaborative wiki and documentation software. An authorization bypass vulnerability in versions 0.70.0 through 0.70.2 exposes restricted child page titles and text snippets through the public search endpoint (`POST /api/search/share-search`) for publicly shared content. This flaw allows unauthenticated users to enumerate and retrieve content that should remain hidden from public share viewers, leading to a confidentiality breach. Version 0.70.3 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33146.json
- https://github.com/docmost/docmost/security/advisories/GHSA-qq4c-8rjr-w42c
- https://nvd.nist.gov/vuln/detail/CVE-2026-33146
