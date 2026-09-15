# [M] Siyuan before v3.8.2 Information Disclosure via Export Preview

## Summary
Severity: Medium
Advisory: CVE-2026-87809
Aliases: GHSA-8wx4-fvqw-f5f8
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87809
Type: osv

## Details
Siyuan before v3.8.2 fails to apply publish-access filtering to embedded blocks before rendering in the /api/export/preview and /api/lute/copyStdMarkdown endpoints. Attackers with reader access can retrieve the full rendered content of private, hidden, or publish-disabled blocks by accessing public documents containing embed queries that select those blocks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87809.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-8wx4-fvqw-f5f8
- https://nvd.nist.gov/vuln/detail/CVE-2026-87809
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-information-disclosure-via-export-preview
