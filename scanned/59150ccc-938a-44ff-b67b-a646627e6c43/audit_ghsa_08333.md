# [C] Kopia: RCE via SSH ProxyCommand Injection

## Summary
Severity: Critical
Advisory: GHSA-2q4c-3mrw-63c3
CVE: CVE-2026-45695
CWE: CWE-306, CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-2q4c-3mrw-63c3
Type: github-advisory

## Affected
- Go: `github.com/kopia/kopia` — affected >=0 <0.23.0

## Details
## Summary

Kopia's HTTP server, when started with `--without-password `, accepts unauthenticated requests to `/api/v1/repo/exists`. The handler forwards an attacker-supplied storage configuration to `blob.NewStorage`. For SFTP backends with `externalSSH: true`, that path constructs a process command line by splitting `sshArguments` on spaces and passes the result directly to `exec.CommandContext("ssh")`. An `-oProxyCommand=<cmd>` token in `sshArguments` causes OpenSSH to invoke `<cmd>` via `$SHELL -c` before any TCP connection is attempted, giving the requester arbitrary command execution as the Kopia process user.

## Analysis

[`internal/server/server_authz_checks.go` lines 61–73](https://github.com/kopia/kopia/blob/v0.22.3/internal/server/server_authz_checks.go#L61-L73):

when the server is started without `--server-username` or `--server-password`, `getAuthenticator()` returns `nil` and `requireUIUser` unconditionally authorizes the request. Every endpoint registered through `handleUIPossiblyNotConnected` becomes accessible without credentials.

[`repo/blob/sftp/sftp_storage.go` lines 448–468](https://github.com/kopia/kopia/blob/v0.22.3/repo/blob/sftp/sftp_storage.go#L448-L468):

`opt.SSHArguments` is populated from the JSON request body (`storage.config.sshArguments`). The string is split only on the literal ASCII space character, there is no shell style tokenizer, no quote handling, and no allowlist. Whatever tokens the caller supplies are appended to the `ssh` argv. 

OpenSSH treats `-oProxyCommand=<value>` as a directive to execute `<value>` via the user's shell (`$SHELL -c <value>`) and pipe the SSH transport over its stdio. The shell invocation happens before SSH attempts a TCP connection, so the command runs even when the target host is unreachable.

## Impact

No user interaction is required. No valid credentials are required. The exploit is a single HTTP request.

## Credits 

This vulnerability was discovered and responsibly disclosed by Daniele Berardinelli.

## Mitigation
https://github.com/kopia/kopia/pull/5354 disallows starting of a server without a password which also listens on a non-loopback interface.

## References
- https://github.com/kopia/kopia/security/advisories/GHSA-2q4c-3mrw-63c3
- https://github.com/kopia/kopia/pull/5354
- https://github.com/kopia/kopia
