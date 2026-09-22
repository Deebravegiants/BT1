# [M] uv is vulnerable to arbitrary file write through entry point names

## Summary
Severity: Medium
Advisory: GHSA-4gg8-gxpx-9rph
CWE: CWE-22
Ecosystem: PyPI, crates.io
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-4gg8-gxpx-9rph
Type: github-advisory

## Affected
- PyPI: `uv` — affected >=0 <0.11.15
- crates.io: `uv` — affected >=0 <0.11.15

## Details
### Impact

In versions of uv prior to 0.11.15, when installing a distribution containing an entry point specification (under `console_scripts` or `gui_scripts`), uv would place the generated entry point according to the given name even if doing so resulted in a path outside of the environment's scripts directory.

A malicious wheel could use this to place an executable outside of the intended environment, including in a directory already present on the user's `PATH`. This could shadow or overwrite an existing executable and potentially result in unexpected code execution under the wheel's control, even if the wheel's installation environment was not explicitly added to `PATH` by the user.

In order to exploit this vulnerability, the attacker must induce their target into installing a malicious wheel.

### Patches

uv 0.11.15 and newer address this vulnerability. Users are encouraged to upgrade to 0.11.15.

### Workarounds

There is no workaround other than upgrading to uv 0.11.15.

## References
- https://github.com/astral-sh/uv/security/advisories/GHSA-4gg8-gxpx-9rph
- https://github.com/astral-sh/uv
