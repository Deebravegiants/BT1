# [M] OpenClaw safeBins grep -e File Read Bypass (stdin-only policy bypass)

## Summary
Severity: Medium
Advisory: GHSA-3xfw-4pmr-4xc5
CVE: CVE-2026-32022
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-3xfw-4pmr-4xc5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
### Summary

OpenClaw `tools.exec.safeBins` had a stdin-only policy bypass for `grep`.
If pattern input was supplied through `-e` / `--regexp`, the validator consumed the pattern as a flag value and still allowed one positional operand. That positional could be a bare filename like `.env`.

### Affected Packages / Versions

- Package: `openclaw` (npm)
- Latest published vulnerable version: `2026.2.19-2`
- Structured vulnerable range: `<= 2026.2.19-2`
- Planned fixed range for next release: `>= 2026.2.21`

### Exploit Preconditions

- `tools.exec.safeBins` must include `grep` (this is opt-in; `grep` is not in the default safe-bin list).
- An actor must be able to invoke exec tooling under that profile.

### Technical Details

`src/infra/exec-safe-bin-policy.ts` configured `grep` with `maxPositional: 1` and allowed `-e` / `--regexp` value flags.
Because `-e` consumes the pattern in flag-value position, the remaining positional budget could be used for a file operand.
Example accepted input in vulnerable builds:

```bash
grep -e SECRET .env
```

That violated the intended stdin-only guarantee for safe bins.

### Impact

With `grep` opt-in enabled, callers could read bare-relative files from the working directory (for example `.env`, `credentials.txt`) in flows expected to be stdin-only.

### Severity Rationale

CVSS v3.1 is set to:
`CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N` (5.3, Medium)

`AC:H` is used because exploitation depends on a non-default configuration (`grep` must be explicitly added to safe bins) in addition to normal low-privilege tool-invocation capability.

### Fix Commit(s)

- `c6ee14d60e4cbd6a82f9b2d74ebeb1e8ee814964`

### Release Process Note

`patched_versions` is pre-set to `>= 2026.2.21` so this advisory is ready to publish after the `2026.2.21` npm release is live.

OpenClaw thanks @athuljayaram for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3xfw-4pmr-4xc5
- https://nvd.nist.gov/vuln/detail/CVE-2026-32022
- https://github.com/openclaw/openclaw/commit/c6ee14d60e4cbd6a82f9b2d74ebeb1e8ee814964
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-file-read-via-grep-e-flag-policy-bypass
