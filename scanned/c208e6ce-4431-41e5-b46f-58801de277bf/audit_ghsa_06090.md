# [H] rclone: PowerShell Smart-Quote Filename Injection Enables SFTP Server-Side Command Execution

## Summary
Severity: High
Advisory: GHSA-2m8m-jhrm-w6j2
CVE: CVE-2026-71312
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-2m8m-jhrm-w6j2
Type: github-advisory

## Affected
- Go: `github.com/rclone/rclone` — affected >=0 <1.75.0

## Details
## 1. Summary

rclone interpolates remote SFTP paths into PowerShell hash commands. Its quoting helper escapes only ASCII apostrophe, although PowerShell accepts four Unicode smart quotes as single-quote delimiters. An attacker-controlled filename can therefore terminate the intended path literal and append PowerShell statements executed as the victim's SSH account.

## 2. Affected Assets & Attack Surface

- Audited commit: `a0c09f1381ae93e2a9a33c529d170186c61ad058`
- Backend: `backend/sftp`
- Relevant code:
  - `backend/sftp/sftp.go:1802-1812` — PowerShell hash commands
  - `backend/sftp/sftp.go:1663-1699` — `Fs.run`
  - `backend/sftp/sftp.go:1988-2067` — `Object.Hash`
  - `backend/sftp/sftp.go:2071-2090` — `quoteOrEscapeShellPath`
- Exposed input: remote filename controlled by an SFTP collaborator, upstream storage source, or other party able to create or rename files.
- Required execution context: PowerShell as the SSH command shell, SSH exec enabled, and server-side hashing invoked.

## 3. Technical Root Cause Analysis

For PowerShell, `quoteOrEscapeShellPath` wraps a path in ASCII apostrophes and doubles only `U+0027`:

```go
return "'" + strings.ReplaceAll(shellPath, "'", "''") + "'", nil
```

Windows PowerShell also treats `U+2018`, `U+2019`, `U+201A`, and `U+201B` as single-quote delimiters. Those characters pass through the rclone encoder and can close the quoted path. The completed string is sent as shell source through an SSH exec request.

The security boundary fails because shell syntax is constructed by string concatenation rather than passing data through a non-code channel.

## 4. Proof-of-Concept & Evidence

- Each of the four Unicode smart quotes was passed through the production quoting function and used to terminate the path literal.
- A harmless injected `Set-Content` statement created a marker file.
- The stronger test invoked the exact production `Object.Hash` path and MD5 PowerShell command against a fake SSH session backed by local PowerShell.
- A valid prefix file allowed `Get-FileHash` to complete; the appended statement then executed.
- The filename used only characters permitted by Windows filesystems and did not depend on slash, colon, pipe, or ASCII apostrophe.
- The focused test passed normally and under Go's race detector.

Reproduction outline:

1. Configure an SFTP remote whose command shell is PowerShell.
2. Enable or autodetect the PowerShell hash command.
3. Place a file whose name contains a smart quote followed by a harmless marker-writing statement and PowerShell comment syntax.
4. Trigger an rclone operation that calculates the remote hash.
5. Observe the marker created with the SSH account's permissions.

## 5. Impact Assessment

Successful exploitation provides arbitrary command execution as the victim's SSH account. This can permit file theft, modification, deletion, credential access, persistence, and lateral movement allowed by that account.

The attacker needs filename-control capability but does not need the victim's SSH credentials or an interactive shell. The rclone user's hash operation supplies the execution step.

## References
- https://github.com/rclone/rclone/security/advisories/GHSA-2m8m-jhrm-w6j2
- https://github.com/rclone/rclone/commit/e122fba1a57641b63a580aa26c026903a84e2e88
- https://github.com/rclone/rclone
- https://github.com/rclone/rclone/releases/tag/v1.75.0
