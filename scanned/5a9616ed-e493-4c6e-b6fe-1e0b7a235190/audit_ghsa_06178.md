# [H] consciousness-explorer / sublinear-time-solver MCP export_state has an arbitrary file write

## Summary
Severity: High
Advisory: GHSA-xc9g-j69q-37xw
CVE: CVE-2026-55609
CWE: CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-xc9g-j69q-37xw
Type: github-advisory

## Affected
- npm: `consciousness-explorer` — affected >=0 <1.1.2
- npm: `sublinear-time-solver` — affected >=0 <1.6.0

## Details
### Impact
An arbitrary file write vulnerability (CWE-73, External Control of File Name or Path) exists in the `consciousness-explorer` component of `sublinear-time-solver`. The MCP `export_state` (and `import_state`) tool accepted a user-supplied `filepath` argument and passed it directly to `fs.writeFileSync` / `fs.readFileSync` without constraining the destination or rejecting path traversal. An attacker able to invoke the MCP tool could write or overwrite any file accessible to the server process (e.g. `~/.ssh/authorized_keys`, application files), leading to integrity loss and potential service disruption.

The same sink class was present in the main solver MCP server (`saveVectorToFile` / `loadVectorFromFile`).

### Affected versions
- `consciousness-explorer` < 1.1.2
- `sublinear-time-solver` < 1.6.0
- `sublinear` (crates.io) < 0.2.0

### Patches
- `consciousness-explorer@1.1.2`
- `sublinear-time-solver@1.6.0`
- `sublinear@0.2.0`

State/vector files are now confined to a dedicated directory (overridable via `$CONSCIOUSNESS_EXPLORER_STATE_DIR` / `$SUBLINEAR_SOLVER_VECTOR_DIR`), a basename-only contract is enforced (rejecting separators, `..`, NUL/control chars, hidden files, and Windows reserved names), and files are opened with `O_NOFOLLOW | O_CLOEXEC` mode `0o600`. Covered by 14 regression tests in `tests/consciousness/safe-path.test.mjs`.

**Breaking change:** callers must now pass a basename, not an absolute path.

### Workarounds
Do not expose the MCP server to untrusted clients; restrict `export_state` to trusted local users; run the server under a low-privilege account with a restricted working directory.

## References
- https://github.com/ruvnet/sublinear-time-solver/security/advisories/GHSA-xc9g-j69q-37xw
- https://github.com/BruceJqs/public_exp/issues/32
- https://github.com/ruvnet/sublinear-time-solver/issues/19
- https://github.com/ruvnet/sublinear-time-solver/pull/20
- https://github.com/ruvnet/sublinear-time-solver/commit/a701296e363192be863e79d788fa268095e3d229
- https://github.com/ruvnet/sublinear-time-solver/commit/ea9a212b69e4449ec443fe088a7aec7546f70b4a
- https://github.com/ruvnet/sublinear-time-solver
- https://github.com/ruvnet/sublinear-time-solver/releases/tag/v1.6.0
