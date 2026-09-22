# [C] Memory corruption in array-tools

## Summary
Severity: Critical
Advisory: GHSA-6wp2-fw3v-mfmc
CVE: CVE-2020-36452
CWE: CWE-908, CWE-909
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-6wp2-fw3v-mfmc
Type: github-advisory

## Affected
- crates.io: `array-tools` — affected >=0 <0.3.2

## Details
An issue was discovered in the array-tools crate before 0.3.2 for Rust. Affected versions of this crate don't guard against panics, so that partially uninitialized buffer is dropped when user-provided `T::clone()` panics in `FixedCapacityDequeLike<T, A>::clone()`. This causes memory corruption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36452
- https://github.com/L117/array-tools/issues/2
- https://github.com/L117/array-tools
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/array-tools/RUSTSEC-2020-0132.md
- https://rustsec.org/advisories/RUSTSEC-2020-0132.html
