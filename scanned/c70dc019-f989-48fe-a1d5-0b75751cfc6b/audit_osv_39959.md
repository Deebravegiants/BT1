# [H] Warp branch selector command injection via Git branch names

## Summary
Severity: High
Advisory: CVE-2026-48719
Aliases: GHSA-hgvx-4xvm-39pw
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-48719
Type: osv

## Details
Warp is an agentic development environment. From 0.2025.08.06.08.12.stable_00 until 0.2026.05.06.15.42.stable_01, Warp contains a command injection in the prompt branch selector. A user who can publish a branch to a Git repository opened in Warp can cause a crafted branch name to be interpreted by the victim's shell if the victim selects that branch from the UI. This vulnerability is fixed in 0.2026.05.06.15.42.stable_01.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48719.json
- https://github.com/warpdotdev/warp/security/advisories/GHSA-hgvx-4xvm-39pw
- https://nvd.nist.gov/vuln/detail/CVE-2026-48719
- https://github.com/warpdotdev/warp/commit/4295ec08d01912fe355351547e541277f29288cd
