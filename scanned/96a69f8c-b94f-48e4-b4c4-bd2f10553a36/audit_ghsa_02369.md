# [C] Potential memory corruption in arrayfire

## Summary
Severity: Critical
Advisory: GHSA-69fv-gw6g-8ccg
CVE: CVE-2018-20998
CWE: CWE-119
Ecosystem: PyPI, crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-69fv-gw6g-8ccg
Type: github-advisory

## Affected
- crates.io: `arrayfire` — affected >=0 <3.6.0
- PyPI: `arrayfire` — affected >=0 <3.6.0

## Details
The attribute repr() added to enums to be compatible with C-FFI caused memory corruption on MSVC toolchain.

arrayfire crates <= version 3.5.0 do not have this issue when used with Rust versions 1.27 or earlier. The issue only started to appear since Rust version 1.28.

The issue seems to be interlinked with which version of Rust is being used.

The issue was fixed in crate 3.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20998
- https://github.com/arrayfire/arrayfire-rust/pull/177
- https://github.com/arrayfire/arrayfire-rust/commit/a5256f3e5e23b83eaad69699e0b04653aba04fb8
- https://github.com/arrayfire/arrayfire-rust
- https://github.com/pypa/advisory-database/tree/main/vulns/arrayfire/PYSEC-2019-144.yaml
- https://rustsec.org/advisories/RUSTSEC-2018-0011.html
