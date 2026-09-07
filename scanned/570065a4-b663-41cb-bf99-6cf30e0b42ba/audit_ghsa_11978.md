# [H] OpenClaw: safeBins static default trusted dirs allow writable-dir binary hijack (`jq`)

## Summary
Severity: High
Advisory: GHSA-5gj7-jf77-q2q2
CVE: CVE-2026-32009
CWE: CWE-426, CWE-428, CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-5gj7-jf77-q2q2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.24

## Details
### Summary
In `openclaw<=2026.2.23`, safe-bin trust in allowlist mode relied on static default trusted directories that included package-manager paths (notably `/opt/homebrew/bin` and `/usr/local/bin`).
When a same-name binary (for example `jq`) is placed in one of those trusted default directories, safe-bin evaluation can be satisfied and execute the attacker-controlled binary.

### Impact
This is an exec allowlist `safeBins` policy bypass that can lead to command execution in the OpenClaw runtime context.
Severity is set to Medium given the required ability to write into trusted host binary directories.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Vulnerable versions: `<= 2026.2.23`
- Patched versions: `>= 2026.2.24` (planned next npm release)
- Latest published npm version at triage time (2026-02-24): `2026.2.23`

### Root Cause
- Default safe-bin trusted directories included package-manager/user-managed paths.
- Trust decision was directory-membership only for resolved executable paths.

### Remediation
- Restrict default safe-bin trusted directories to immutable system paths: `/bin`, `/usr/bin`.
- Require explicit operator opt-in for package-manager/user paths via `tools.exec.safeBinTrustedDirs`.

### Fix Commit(s)
- `b67e600bff696ff2ed9b470826590c0ce6b3bb0a`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.24`).
Once npm release `2026.2.24` is published, this advisory should be ready for publish without additional version edits.

OpenClaw thanks @tdjackey for reporting.


### Publication Update (2026-02-25)
`openclaw@2026.2.24` is published on npm and contains the fix commit(s) listed above. This advisory now marks `>= 2026.2.24` as patched.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5gj7-jf77-q2q2
- https://nvd.nist.gov/vuln/detail/CVE-2026-32009
- https://github.com/openclaw/openclaw/commit/b67e600bff696ff2ed9b470826590c0ce6b3bb0a
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-binary-hijacking-via-static-default-trusted-directories-in-safebins
