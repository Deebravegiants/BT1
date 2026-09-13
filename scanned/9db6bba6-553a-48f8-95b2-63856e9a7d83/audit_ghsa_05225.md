# [M] rattler has an entry-point path traversal in noarch:python install (arbitrary file write)

## Summary
Severity: Medium
Advisory: GHSA-q53q-5r4j-5729
CVE: CVE-2026-47425
CWE: CWE-22, CWE-73
Ecosystem: PyPI, crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-q53q-5r4j-5729
Type: github-advisory

## Affected
- crates.io: `rattler` — affected >=0 <0.43.2
- PyPI: `py-rattler` — affected >=0 <0.24.0

## Details
## Summary

`EntryPoint::FromStr` in `rattler_conda_types` performs only `.trim()` on the `command` field before the linker joins it onto the install prefix and writes an executable Python script. A malicious `noarch:python` package can ship an `info/link.json` with an entry-point name containing `..`, `/`, `\`, or an absolute path; the resulting file is written outside the prefix (or clobbers an existing in-prefix entry-point such as `bin/pip`) with mode `0o775` on Unix and a copied launcher `.exe` on Windows. This affects the default install path of `pixi install`, `rattler-build`, some methods in `py-rattler`, and any other consumer of the `rattler` install crate; no flag or post-link-script opt-in is involved.

Resolved in https://github.com/conda/rattler/pull/2445, released in rattler 0.43.2.

## Affected

- Repository: https://github.com/conda/rattler
- Commit: `a0e61a33da8b9d6de712fab2a879fa9da977e6e3` (HEAD at audit time, 2026-05-13 release)
- Downstream consumers reached through the same code path: `prefix-dev/pixi` @ `e640477`
- pixi 0.69.0 and rattler-build 0.65.0 fix this issue

## Researcher

Berkant Koc <me@berkoc.com>
PGP: 0C588DFD76204987284213EA0AC529C41F8AA5D6

## References
- https://github.com/conda/rattler/security/advisories/GHSA-q53q-5r4j-5729
- https://github.com/conda/rattler/pull/2445
- https://github.com/conda/rattler
