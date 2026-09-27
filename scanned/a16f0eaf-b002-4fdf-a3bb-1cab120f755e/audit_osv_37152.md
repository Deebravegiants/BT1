# [H] Ghostfolio: Time-Based Blind SQL Injection in Manual Asset Import

## Summary
Severity: High
Advisory: CVE-2026-28785
Aliases: GHSA-m5cc-7jw5-34xp
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-28785
Type: osv

## Details
Ghostfolio is an open source wealth management software. Prior to version 2.244.0, by bypassing symbol validation, an attacker can execute arbitrary SQL commands via the getHistorical() method, potentially allowing them to read, modify, or delete sensitive financial data for all users in the database. This issue has been patched in version 2.244.0.

## References
- https://github.com/ghostfolio/ghostfolio/releases/tag/2.244.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28785.json
- https://github.com/ghostfolio/ghostfolio/security/advisories/GHSA-m5cc-7jw5-34xp
- https://nvd.nist.gov/vuln/detail/CVE-2026-28785
