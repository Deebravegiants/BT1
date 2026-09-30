# [M] CVE-2026-41526

## Summary
Severity: Medium
Advisory: CVE-2026-41526
CVSS: 6.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/CVE-2026-41526
Type: osv

## Details
In KDE KCoreAddons before 6.25, KShell::quoteArgs is intended to safely quote arguments so that they can be passed to a shell command. This parsing does not adequately handle metacharacters, leading to an escape from the shell. All applications relying on this method in a security-critical path to handle user input are affected and could be exploited. In particular, because sendInput() sends a string to a terminal, a control character such as \x01 can be used during injection.

## References
- https://github.com/KDE/kcoreaddons/blob/50d360736c399502fedf203e95482b0d0e5a3ea2/src/lib/util/kshell.h#L168
- https://github.com/KDE/kcoreaddons/blob/50d360736c399502fedf203e95482b0d0e5a3ea2/src/lib/util/kshell.h#L43-L49
- https://github.com/KDE/kcoreaddons/releases/tag/v6.25.0
- https://invent.kde.org/frameworks/kcoreaddons/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41526.json
- https://kde.org/info/security/advisory-20260427-1.txt
- https://nvd.nist.gov/vuln/detail/CVE-2026-41526
