# [C] Vim: Arbitrary Code Execution via Netrw Menu Construction

## Summary
Severity: Critical
Advisory: CVE-2026-73078
Aliases: GHSA-rcr7-f3wr-22r2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73078
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0840, runtime/plugin/netrwPlugin.vim loads netrw and runtime/pack/dist/opt/netrw/autoload/netrw.vim constructs Bookmarks, History, and Targets menu entries by interpolating attacker-controlled directory paths into executed :menu commands. s:NetrwBookmarkMenu(), s:NetrwTgtMenu(), g:netrw_menu_escape, EX_TRLBAR, and netrw#MakeTgt() fail to neutralize the | command separator or single quotes at five construction sites, allowing a crafted path browsed or bookmarked in GUI Vim to execute arbitrary Ex and operating-system commands. This issue is fixed in version 9.2.0840.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73078.json
- https://github.com/vim/vim/security/advisories/GHSA-rcr7-f3wr-22r2
- https://nvd.nist.gov/vuln/detail/CVE-2026-73078
- https://github.com/vim/vim/commit/29c6fd090d4520592f8be7d9ec81190edf25ef69
