# [H] Docmost affected by an Arbitrary File Write via Zip Import Feature (ZipSlip)

## Summary
Severity: High
Advisory: CVE-2026-22249
Aliases: GHSA-54pm-hqxm-54wg
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-01-15
Source: https://osv.dev/vulnerability/CVE-2026-22249
Type: osv

## Details
Docmost is an open-source collaborative wiki and documentation software. From 0.21.0 to before 0.24.0, Docmost is vulnerable to Arbitrary File Write via Zip Import Feature (ZipSlip). In apps/server/src/integrations/import/utils/file.utils.ts, there are no validation on filename. This vulnerability is fixed in 0.24.0.

## References
- https://github.com/docmost/docmost/releases/tag/v0.24.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22249.json
- https://github.com/docmost/docmost/security/advisories/GHSA-54pm-hqxm-54wg
- https://nvd.nist.gov/vuln/detail/CVE-2026-22249
- https://github.com/docmost/docmost/commit/c3b350d943108552e20654580005cd6f6c78ab05
- https://github.com/docmost/docmost/pull/1753
