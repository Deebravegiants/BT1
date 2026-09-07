# [M] rclone: FTP Command Arguments Permit CRLF Injection When Custom Encoding Preserves Newlines

## Summary
Severity: Medium
Advisory: GHSA-8c48-q9wj-3w37
CVE: CVE-2026-71311
CWE: CWE-93
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-8c48-q9wj-3w37
Type: github-advisory

## Affected
- Go: `github.com/rclone/rclone` — affected >=0 <1.75.0

## Details
## 1. Summary

A valid but nondefault FTP filename encoding can restore raw CR/LF immediately before an attacker-controlled path is interpolated into the line-oriented FTP control channel. The dependency does not reject CR or LF in command arguments, so a filename can inject an independent authenticated command. A real test server observed the injected `DELE` command.

The default FTP encoding and the configuration-wizard examples include `Ctl` and are not vulnerable to the demonstrated filename. A manual custom encoding that omits `Ctl`/`CrLf` is mandatory and is reflected as High attack complexity. The credible trust boundary is a lower-trust source namespace feeding a more-privileged FTP destination: if the attacker already has equivalent rights on that destination, the report establishes a bug but no privilege gain. Protocol framing must still be enforced at the command sink because a filename-compatibility encoder is not a safe substitute for command-argument validation.

## 2. Affected Assets & Attack Surface

- Verified rclone revision: `a0c09f1381ae93e2a9a33c529d170186c61ad058` (`v1.74.0-240-ga0c09f138`)
- Current-master check: the relevant paths remained present at commit `961266888fe797390c535386f3b3aa46f4853602` on 2026-07-18
- rclone FTP encoding: `backend/ftp/ftp.go:232-248`, `768-785`
- Encoder masks/conversion: `lib/encoder/encoder.go:36-68`, `121-152`, `1144-1165`
- FTP command sinks: `backend/ftp/ftp.go:1071-1173`, `1309-1428`
- Dependency: `github.com/jlaffaye/ftp@v0.2.1-0.20251026020404-6602e981a1bb`
- Dependency command formatting: `ftp.go:604-610`, with path-bearing callers at `ftp.go:893-947`, `1010-1026`, and `1069-1080`
- Preconditions: an attacker can create a filename in a source namespace, the victim copies/syncs it to an FTP destination with greater authority, and that destination uses a manually configured encoding that leaves CR/LF raw
- Platform note: Unix and some remote backends can supply newline-bearing names; a local Windows source cannot create the demonstrated filename

## 3. Technical Root Cause Analysis

Rclone represents control characters safely in its internal Standard encoding. Immediately before an FTP operation, `FromStandardPath` decodes that representation and applies the configured backend mask. If the mask omits `Ctl`/`CrLf`, raw newlines are restored. The dependency then formats the resulting argument onto a CRLF-delimited control stream through `textproto.Conn.Cmd` without validating it. Reversible filename representation is therefore being used as the only protection for a protocol-command boundary.

## 4. Proof-of-Concept & Evidence

The source filename was equivalent to:

```text
victim\r\nDELE other-secret\r\nNOOP
```

With the default encoding, no raw newline reached the command. With the valid nondefault configuration `encoding = Slash`, `FromStandardPath` restored raw CRLF. During a real FTP path operation, the server parsed `DELE other-secret` as an independent authenticated command. This establishes injection, not merely unsafe serialization. The test did not establish confidentiality impact or operating-system command execution.

## 5. Impact Assessment

Injected commands run with the configured FTP account's permissions. Demonstrated direct impact is deletion of a different path, with corresponding integrity and availability loss inside that account. Other FTP filesystem commands may be reachable, but confidentiality and arbitrary operating-system command execution are not claimed. The privilege-boundary case requires the victim's FTP account to have more authority than the attacker has in the source namespace.

## 6. Remediation Guidance

- Reject CR and LF in every FTP command argument at the lowest command-construction boundary.
- Apply the check to paths, usernames, passwords, rename arguments, and all other formatted fields.
- Return an error rather than silently normalizing an unsafe argument.
- Keep the default encoder protection as defense in depth and reject an FTP encoding configuration that can restore CR/LF.
- Add end-to-end tests for CR, LF, CRLF, and each path command.

## References
- https://github.com/rclone/rclone/security/advisories/GHSA-8c48-q9wj-3w37
- https://github.com/rclone/rclone/commit/1df2b70753286c1dfe8366078cbedfdf7f96472c
- https://github.com/rclone/rclone
- https://github.com/rclone/rclone/releases/tag/v1.75.0
