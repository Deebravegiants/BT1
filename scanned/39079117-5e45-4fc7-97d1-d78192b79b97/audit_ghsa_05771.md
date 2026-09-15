# [M] Snipe-IT has CSV formula injection in Activity Report export

## Summary
Severity: Medium
Advisory: GHSA-whrx-mmgr-gpcf
CVE: CVE-2026-55452
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-whrx-mmgr-gpcf
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.2

## Details
### Impact
In Snipe-IT v8.6.1 and lower, `Actionlog::logaction()` stores the request User-Agent header in user_agent. That value is later included in the Activity Report CSV export by `ReportsController::postActivityReport()` and written with plain `fputcsv()`.

A low-privileged authenticated user can set a formula-like User-Agent, perform a logged action, and have that value stored in the activity log. If an admin or report viewer later exports the Activity Report and opens it in spreadsheet software, the formula may execute.

Example payload:

`User-Agent: =HYPERLINK("https://example.com/","click")`

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-whrx-mmgr-gpcf
- https://nvd.nist.gov/vuln/detail/CVE-2026-55452
- https://github.com/grokability/snipe-it/commit/7b7d2c87fbc965a7933b1bf9e3f2c331b8c8e19c
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.5.0
