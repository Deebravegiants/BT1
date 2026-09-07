# [H] SSH/SCP option injection allowing local RCE in @aiondadotcom/mcp-ssh

## Summary
Severity: High
Advisory: GHSA-p4h8-56qp-hpgv
CWE: CWE-78, CWE-88
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-p4h8-56qp-hpgv
Type: github-advisory

## Affected
- npm: `@aiondadotcom/mcp-ssh` — affected >=0 <1.3.5

## Details
## Impact

A crafted `hostAlias` argument such as `-oProxyCommand=...` was passed to `ssh`/`scp` without an argument terminator. SSH interprets arguments starting with `-` as options regardless of position, so the option-injection caused SSH to execute the attacker-supplied `ProxyCommand` **locally** on the machine running the MCP server — before any network connection. This bypassed the documented protection of `# @password:` annotations and exposed local SSH keys, browser cookies, other MCP server credentials, and anything else readable by the server process.

A second local-RCE vector existed on Windows: `spawn(..., { shell: true })` was used so that `ssh.exe`/`scp.exe` could be found via `PATH`. With `shell: true`, every argument is re-parsed by `cmd.exe`, so shell metacharacters (`&`, `|`, `^`, `>`, `"`, `;`, …) in `hostAlias`, `command`, `localPath` or `remotePath` would have been interpreted by `cmd.exe` and could have triggered arbitrary local command execution on Windows.

The MCP server runs locally over STDIO, but the LLM driving it is not trusted: its tool arguments can be steered by **prompt injection** from any untrusted text the LLM ingests (web pages, e-mails, repository files, output of other MCP servers). The attack does not require a malicious user — only that the LLM ingests attacker-controlled text at any point during the session.

## Patches

Fixed in **1.3.5**.

- Add `--` argument terminator to all `ssh`/`scp` invocations.
- Strict whitelist for `hostAlias` (rejects leading `-` and shell metacharacters).
- Known-host check: every `hostAlias` must be defined in `~/.ssh/config` (including `Include` directives) or present in `~/.ssh/known_hosts`.
- Resolve `ssh.exe`/`scp.exe` to absolute paths and use `shell: false` everywhere on Windows.

## Workarounds

None. Upgrade to 1.3.5.

## Credit

Reported by Pico (@piiiico) as part of an MCP server security audit.

## References
- https://github.com/AiondaDotCom/mcp-ssh/security/advisories/GHSA-p4h8-56qp-hpgv
- https://github.com/AiondaDotCom/mcp-ssh/issues/9
- https://github.com/AiondaDotCom/mcp-ssh
- https://github.com/AiondaDotCom/mcp-ssh/releases/tag/1.3.5
