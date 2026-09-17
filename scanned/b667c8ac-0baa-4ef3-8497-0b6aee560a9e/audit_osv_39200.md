# [H] Zed: Remote Command Injection via Unquoted Environment Variable Keys (SSH / WSL Remote)

## Summary
Severity: High
Advisory: CVE-2026-44461
Aliases: GHSA-63qj-jc2q-7hg5
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-44461
Type: osv

## Details
Zed is a code editor. Prior to 0.227.1, Zed builds SSH/WSL remote commands as a shell command string that starts with exec env ..., but environment variable keys are inserted without shell quoting or validation. If an attacker can control an environment variable key (for example via project terminal settings), shell expansions in the key (such as $(...)) are evaluated by the remote shell when a terminal is opened. This can lead to arbitrary command execution on the remote host under the victim user's account. This vulnerability is fixed in 0.227.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44461.json
- https://github.com/zed-industries/zed/security/advisories/GHSA-63qj-jc2q-7hg5
- https://nvd.nist.gov/vuln/detail/CVE-2026-44461
