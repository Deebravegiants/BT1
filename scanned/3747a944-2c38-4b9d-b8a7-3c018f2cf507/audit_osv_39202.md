# [H] Zed: Allowlist Bypass via Environment Variable Injection in Terminal Tool Permissions

## Summary
Severity: High
Advisory: CVE-2026-44463
Aliases: GHSA-c3g6-c3ff-69cg
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-44463
Type: osv

## Details
Zed is a code editor. Prior to 0.229.0, Zed's terminal tool permission system can be bypassed by prepending environment variable assignments to allowlisted commands, hijacking program behavior (e.g., PAGER) to execute arbitrary code. This vulnerability is fixed in 0.229.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44463.json
- https://github.com/zed-industries/zed/security/advisories/GHSA-c3g6-c3ff-69cg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44463
