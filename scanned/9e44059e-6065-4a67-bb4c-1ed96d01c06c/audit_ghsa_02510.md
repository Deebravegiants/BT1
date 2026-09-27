# [C] Unaligned memory access in rand_core

## Summary
Severity: Critical
Advisory: GHSA-mmc9-pwm7-qj5w
CVE: CVE-2020-25576
CWE: CWE-704
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-mmc9-pwm7-qj5w
Type: github-advisory

## Affected
- crates.io: `rand_core` — affected >=0.4.0 <0.4.2
- crates.io: `rand_core` — affected >=0 <0.3.1

## Details
### Impact
Affected versions of this crate violated alignment when casting byte slices to integer slices, resulting in undefined behavior. `rand_core::BlockRng::next_u64` and `rand_core::BlockRng::fill_bytes` are affected.

### Patches
The flaw was corrected by Ralf Jung and Diggory Hardy for `rand_core >= 0.4.2`.

### Workarounds
None.

### References
See [Rand's changelog](https://github.com/rust-random/rand/blob/master/rand_core/CHANGELOG.md#050---2019-06-06).

### For more information
If you have any questions or comments about this advisory, [open an issue in the Rand repository](https://github.com/rust-random/rand/issues/new/choose).

## References
- https://github.com/rust-random/rand/security/advisories/GHSA-mmc9-pwm7-qj5w
- https://github.com/rust-random/rand
- https://github.com/rust-random/rand/blob/master/rand_core/CHANGELOG.md#050---2019-06-06
- https://rustsec.org/advisories/RUSTSEC-2019-0035.html
