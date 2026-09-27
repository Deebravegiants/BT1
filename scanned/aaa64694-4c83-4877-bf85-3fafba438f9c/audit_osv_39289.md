# [H] Tabby auto-confirms ZMODEM detection on terminal output, leading to shell command execution from displayed file content under fish, bash, and zsh

## Summary
Severity: High
Advisory: CVE-2026-45036
Aliases: GHSA-qr3x-j8g9-xhf6
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-45036
Type: osv

## Details
Tabby (formerly Terminus) is a highly configurable terminal emulator. Prior to 1.0.233, Tabby before 1.0.233 automatically confirms ZMODEM protocol detection on all terminal session output without user interaction, enabling shell command execution when a user displays attacker-controlled content. The ZModemMiddleware in tabby-terminal consumes all session output through a Zmodem.Sentry, and when a ZMODEM ZRQINIT header is detected, unconditionally calls detection.confirm() and writes a fixed ZRINIT response ( **\x18B0100000023be50\r\n\x11) back into the active PTY as input. When the process that triggered the detection (e.g., cat) exits, the injected bytes are consumed by the user's shell as a command line. Under fish (default configuration), the ** prefix triggers recursive glob expansion against the current directory, allowing an attacker-placed executable at a matching nested path (e.g., d/xB0100000023be50) to be executed by relative pathname without relying on PATH. Under bash and zsh, a secondary xterm.js terminal color-query feedback (OSC 10) can be combined in the same file to inject a slash-containing command word that similarly bypasses PATH resolution. An attacker can exploit this by providing a crafted file (e.g., in a cloned Git repository) that a user displays with cat, achieving code execution with no interaction beyond viewing the file. This vulnerability is fixed in 1.0.233.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45036.json
- https://github.com/Eugeny/tabby/security/advisories/GHSA-qr3x-j8g9-xhf6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45036
