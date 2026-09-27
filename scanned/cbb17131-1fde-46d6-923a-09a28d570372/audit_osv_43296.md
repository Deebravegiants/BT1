# [H] Claude Code Templates: Unauthenticated OS command injection (RCE) in Claude Code Studio server (--studio)

## Summary
Severity: High
Advisory: CVE-2026-73222
Aliases: GHSA-79wm-x847-7cvg
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73222
Type: osv

## Details
Claude Code Templates is a CLI tool for configuring and monitoring Claude Code. Prior to 1.29.4, the Claude Code Studio server launched by the --studio option in cli-tool/src/sandbox-server.js binds to all interfaces on port 3444, permits cross-origin requests, and requires no authentication. The POST /api/execute endpoint passes the prompt request-body field to executeLocalTask(), and POST /api/install-agent passes the agentName request-body field to a child process. The same unsafe agent field path is reachable from /api/execute through checkAndInstallAgent(). These attacker-controlled values reach child_process.spawn() with shell execution enabled, causing Node.js to construct a shell command in which metacharacters are interpreted. An attacker who can reach the port directly, or who convinces a developer running Studio to visit a malicious website, can execute arbitrary operating-system commands with the developer's privileges and compromise source code, credentials, and local data. This issue is fixed in version 1.29.4.

## References
- https://github.com/davila7/claude-code-templates/blob/main/CHANGELOG.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73222.json
- https://github.com/davila7/claude-code-templates/security/advisories/GHSA-79wm-x847-7cvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-73222
- https://github.com/davila7/claude-code-templates/commit/bc4618b07232633c1c0aac12a43e436268d31783
