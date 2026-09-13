# [H] FreePBX: Authenticated Framework AUTHTYPE Can Be Restored From a Crafted Backup

## Summary
Severity: High
Advisory: CVE-2026-73661
Aliases: GHSA-f6hc-rqxg-ch86
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73661
Type: osv

## Details
FreePBX is an open source IP PBX. Prior to 16.0.47 and 17.0.30, the FreePBX Framework module permits a crafted backup to restore the hidden AUTHTYPE setting with the value none through runRestore() in amp_conf/htdocs/admin/libraries/Builtin/Restore.php. An authenticated user with sufficient backup-restore access or write access to backup files can thereby disable FreePBX authentication during restoration, bypassing the user-interface removal of AUTHTYPE=none. This issue is fixed in versions 16.0.47 and 17.0.30.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73661.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-f6hc-rqxg-ch86
- https://nvd.nist.gov/vuln/detail/CVE-2026-73661
- https://github.com/FreePBX/framework/commit/0591581654bc269df05cbb7093645d6934d4d861
- https://github.com/FreePBX/framework/commit/ea684be89abb393d1aff7f979d5fd751ff338dfd
