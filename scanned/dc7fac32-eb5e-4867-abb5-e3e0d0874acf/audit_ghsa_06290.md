# [M] Zoo Design Studio: Memory-corruption in memory handling of lib-kcl

## Summary
Severity: Medium
Advisory: GHSA-mc9m-6fm9-pghc
CWE: CWE-362, CWE-416
Ecosystem: PyPI, crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-mc9m-6fm9-pghc
Type: github-advisory

## Affected
- PyPI: `zoo-kcl` — affected >=0 <0.3.153
- crates.io: `kcl-lib` — affected >=0 <0.2.153

## Details
A race condition in kcl-lib can result in a use-after-free when accessing environments concurrently. During Vec reallocation, the previous buffer containing Box pointers is freed and replaced. A concurrent get_env operation that has already loaded a pointer to the old buffer may subsequently index into freed memory and retrieve a stale or corrupted Pin<Box<Environment>>.

## References
- https://github.com/KittyCAD/modeling-app/security/advisories/GHSA-mc9m-6fm9-pghc
- https://github.com/KittyCAD/modeling-app
