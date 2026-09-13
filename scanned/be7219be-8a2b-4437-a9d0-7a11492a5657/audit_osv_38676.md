# [H] Skim: Arbitrary code execution via pull_request_target fork checkout in pr.yml

## Summary
Severity: High
Advisory: CVE-2026-41414
Aliases: GHSA-9g93-rxr5-xhqw
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-41414
Type: osv

## Details
Skim is a fuzzy finder designed to through files, lines, and commands. The generate-files job in .github/workflows/pr.yml checks out attacker-controlled fork code and executes it via cargo run, with access to SKIM_RS_BOT_PRIVATE_KEY and GITHUB_TOKEN (contents:write). No gates prevent exploitation - any GitHub user can trigger this by opening a pull request from a fork. This vulnerability is fixed with commit bf63404ad51985b00ed304690ba9d477860a5a75.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41414.json
- https://github.com/skim-rs/skim/security/advisories/GHSA-9g93-rxr5-xhqw
- https://nvd.nist.gov/vuln/detail/CVE-2026-41414
- https://github.com/skim-rs/skim/commit/bf63404ad51985b00ed304690ba9d477860a5a75
- https://drive.google.com/file/d/1Gj7ziTK42YWXYoQgTbis_rMitHR59J6F/view
