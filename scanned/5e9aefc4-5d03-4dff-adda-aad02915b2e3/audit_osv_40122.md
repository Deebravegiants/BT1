# [M] Hermes WebUI < 0.51.303 TOCTOU Race Condition via git_discard

## Summary
Severity: Medium
Advisory: CVE-2026-49958
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:A/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-49958
Type: osv

## Details
Hermes WebUI before version 0.51.303 contains a time-of-check time-of-use (TOCTOU) race condition vulnerability in the git_discard function within api/workspace_git.py that allows attackers to delete files outside the configured workspace boundary by replacing a validated path component with a symlink after validation but before deletion. Attackers can substitute a workspace-controlled path component with a symlink pointing to an external directory between the safe_resolve_ws() validation step and the subsequent Path.unlink() or shutil.rmtree() deletion call, causing the delete operation to follow the symlink and remove arbitrary files outside the workspace.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49958.json
- https://github.com/nesquena/hermes-webui/releases/tag/v0.51.303
- https://nvd.nist.gov/vuln/detail/CVE-2026-49958
- https://www.vulncheck.com/advisories/hermes-webui-toctou-race-condition-via-git-discard
- https://github.com/nesquena/hermes-webui/pull/3702
- https://github.com/nesquena/hermes-webui/pull/3756
- https://github.com/nesquena/hermes-webui/commit/4580f584964d640b95c4ffc9245a21ab926bec73
- https://github.com/nesquena/hermes-webui
