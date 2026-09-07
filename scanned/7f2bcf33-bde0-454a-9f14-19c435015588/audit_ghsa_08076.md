# [M] OpenClaw affected by denial of service through unguarded archive extraction allowing high expansion/resource abuse (ZIP/TAR)

## Summary
Severity: Medium
Advisory: GHSA-h89v-j3x9-8wqj
CVE: CVE-2026-28452
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-h89v-j3x9-8wqj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14
- npm: `clawdbot` — affected >=0

## Details
## Summary
Archive extraction lacked strict resource budgets, allowing high-expansion ZIP/TAR archives to consume excessive CPU/memory/disk during install/update flows.

## Affected Packages / Versions
- openclaw (npm): <= 2026.2.13
- clawdbot (npm): <= 2026.1.24-3

## Details
Affected component: `src/infra/archive.ts` (`extractArchive`).

The extractor now enforces resource budgets (entry count and extracted byte limits; ZIP also enforces a compressed archive size limit) and rejects over-budget archives.

## Fix Commit(s)
- openclaw/openclaw@d3ee5deb87ee2ad0ab83c92c365611165423cb71
- openclaw/openclaw@5f4b29145c236d124524c2c9af0f8acd048fbdea

## Release Process Note
This advisory will be updated with patched versions once the next npm release containing the fix is published.

## Credits
Thanks @vincentkoc for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h89v-j3x9-8wqj
- https://nvd.nist.gov/vuln/detail/CVE-2026-28452
- https://github.com/openclaw/openclaw/commit/5f4b29145c236d124524c2c9af0f8acd048fbdea
- https://github.com/openclaw/openclaw/commit/d3ee5deb87ee2ad0ab83c92c365611165423cb71
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
- https://www.vulncheck.com/advisories/openclaw-denial-of-service-via-unguarded-archive-extraction-in-extractarchive
