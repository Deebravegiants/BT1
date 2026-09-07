# [M] Gryph Agents Payload Filter Fails to Strip Tool Payload for Sensitive Content

## Summary
Severity: Medium
Advisory: GHSA-f3jg-756w-gm35
CVE: CVE-2026-45046
CWE: CWE-212
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-f3jg-756w-gm35
Type: github-advisory

## Affected
- Go: `github.com/safedep/gryph` — affected >=0 <0.7.0

## Details
Gryph implements logging levels that determine what content is logged to a local sqlite database. The README incorrectly mentions that the default log level is minimal while it is standard.  Source code review shows sensitive `file-write` content remains in the stored `payload` as `ContentPreview`, `OldString`, or `NewString` at the default `standard` logging level and at `full`. This leads to logging of potentially sensitive file content in the local sqlite database, violating Gryphs sensitive file filter and log level contracts. 

### Impact

Potentially sensitive data accessed or written by coding agents may be logged to local sqlite database. Users of Gryph are affected ONLY if their local sqlite database is stolen or exported to remote system with the assumption that no sensitive data is logged.

### Patches

Fixed in v0.7.0

## References
- https://github.com/safedep/gryph/security/advisories/GHSA-f3jg-756w-gm35
- https://nvd.nist.gov/vuln/detail/CVE-2026-45046
- https://github.com/safedep/gryph
- https://github.com/safedep/gryph/releases/tag/v0.7.0
