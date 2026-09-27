# [M] Zed does not show Parameter Values for MCP Tool Calls. Users cannot detect tool poisoning.

## Summary
Severity: Medium
Advisory: CVE-2026-25805
Aliases: GHSA-f2g4-87h6-4pxq
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-10
Source: https://osv.dev/vulnerability/CVE-2026-25805
Type: osv

## Details
Zed is a multiplayer code editor. Prior to 0.219.4, Zed does not show with which parameters a tool is being invoked, when asking for allowance. Further it does not show after the tool was being invoked, which parameters were used. Thus, maybe unwanted or even malicious values could be used without the user having a chance to notice it. Patched in Zed Editor 0.219.4 which includes expandable tool call details.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25805.json
- https://github.com/zed-industries/zed/security/advisories/GHSA-f2g4-87h6-4pxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-25805
