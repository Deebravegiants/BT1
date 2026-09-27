# [M] Zed: Allowlist Bypass via Bash Variable Expansion Chain in Terminal Tool Permissions

## Summary
Severity: Medium
Advisory: CVE-2026-44462
Aliases: GHSA-rqq3-p6x4-q866
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:L)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-44462
Type: osv

## Details
Zed is a code editor. Prior to 0.229.0, Zed's terminal tool permission system can be bypassed via bash variable expansion chaining (${var@P}), allowing arbitrary command execution under an allowlisted command prefix. This vulnerability is fixed in 0.229.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44462.json
- https://github.com/zed-industries/zed/security/advisories/GHSA-rqq3-p6x4-q866
- https://nvd.nist.gov/vuln/detail/CVE-2026-44462
