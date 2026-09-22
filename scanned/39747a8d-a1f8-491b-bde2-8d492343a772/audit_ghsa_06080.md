# [M] Ember has unneutralized terminal escape/control sequences from Caddy logs injected into the operator's TUI

## Summary
Severity: Medium
Advisory: GHSA-x3g7-qrwc-f6c5
CVE: CVE-2026-54162
CWE: CWE-150
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-x3g7-qrwc-f6c5
Type: github-advisory

## Affected
- Go: `github.com/alexandre-daubois/ember` — affected >=0 <1.4.2

## Details
## Summary

Ember's interactive TUI renders fields taken from the monitored Caddy server's access logs — most notably the request URI — straight to the operator's terminal without neutralising terminal escape or control sequences (CWE-150). Those log fields are populated from arbitrary, unauthenticated HTTP requests, so any remote client can embed ANSI/OSC/CSI control bytes that the operator's terminal emulator interprets when the log row is displayed. The bytes survive the whole pipeline: Caddy escapes them into its JSON access log as unicode escapes, ember's `ParseLogLine` decodes them back to raw `0x1b`/`0x07` bytes, and the row formatters concatenate them into the bubbletea `View()` output with no encoding before they reach `os.Stdout`.

## Impact

An **unauthenticated, remote** attacker who can send HTTP requests to the Caddy server that ember monitors can inject terminal escape sequences into the operator's TUI. The trigger is a single ordinary HTTP request with control bytes in the request target. It requires no authentication; because the payload is reflected through Caddy's normal access log, it works even when ember's log listener is bound only to loopback. When the operator views the Logs tab — ember's default, zero-config mode — the terminal emulator interprets the injected sequences. Broadly-supported, demonstrated impact includes:

- **Monitoring-dashboard spoofing** — CSI cursor/erase/scroll sequences forge or hide log rows so the operator misjudges the monitored server's state.
- **Clipboard hijacking (OSC 52)** — attacker-chosen text is written into the operator's system clipboard, staging a payload the operator may later paste into a shell.
- **Window-title spoofing (OSC 0/2)** — to support social engineering.

The impact ceiling depends on the operator's terminal emulator and usually requires a further operator action (e.g. a paste) to fully escalate; this is not general-case RCE, though specific terminal emulators have historically escalated escape sequences further. The Certificates and Routes tabs share the same unneutralised render path as secondary sinks. The `--json`/`--once` and daemon (`--expose`) modes are not affected, as they do not render to an interactive terminal.

## References

- https://github.com/alexandre-daubois/ember/blob/main/internal/ui/logtable.go#L18 — the unneutralised render helper (`fitCellLeft`) and row formatters (the sink)
- https://github.com/alexandre-daubois/ember/blob/main/internal/fetcher/lognetlistener.go — the unauthenticated TCP access-log listener (input source)
- https://github.com/alexandre-daubois/ember/blob/main/internal/fetcher/logentry.go — `ParseLogLine`, where the JSON decode restores raw control bytes
- https://cwe.mitre.org/data/definitions/150.html — CWE-150: Improper Neutralization of Escape, Meta, or Control Sequences

## References
- https://github.com/alexandre-daubois/ember/security/advisories/GHSA-x3g7-qrwc-f6c5
- https://github.com/alexandre-daubois/ember/commit/fcb7160e58dba58d6f9b5033cc312fdedc8c9f6b
- https://github.com/alexandre-daubois/ember
- https://github.com/alexandre-daubois/ember/releases/tag/v1.4.2
