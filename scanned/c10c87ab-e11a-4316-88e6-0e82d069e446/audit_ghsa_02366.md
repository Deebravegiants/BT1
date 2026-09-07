# [H] crossbeam-channel Undefined Behavior before v0.4.4

## Summary
Severity: High
Advisory: GHSA-v5m7-53cv-f3hx
CVE: CVE-2020-15254
CWE: CWE-119, CWE-401
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-v5m7-53cv-f3hx
Type: github-advisory

## Affected
- crates.io: `crossbeam-channel` — affected >=0.4.3 <0.4.4

## Details
### Impact

The affected version of this crate's the `bounded` channel incorrectly assumes that `Vec::from_iter` has allocated capacity that same as the number of iterator elements. `Vec::from_iter` does not actually guarantee that and may allocate extra memory. The destructor of the `bounded` channel reconstructs `Vec` from the raw pointer based on the incorrect assumes described above. This is unsound and causing deallocation with the incorrect capacity when `Vec::from_iter` has allocated different sizes with the number of iterator elements.

### Patches

This has been fixed in crossbeam-channel 0.4.4.

We recommend users to upgrade to 0.4.4.

### References

See https://github.com/crossbeam-rs/crossbeam/pull/533, https://github.com/crossbeam-rs/crossbeam/issues/539, and https://github.com/RustSec/advisory-db/pull/425 for more details.

### License

This advisory is in the public domain.

## References
- https://github.com/crossbeam-rs/crossbeam/security/advisories/GHSA-v5m7-53cv-f3hx
- https://nvd.nist.gov/vuln/detail/CVE-2020-15254
- https://github.com/crossbeam-rs/crossbeam/issues/539
- https://github.com/RustSec/advisory-db/pull/425
- https://github.com/crossbeam-rs/crossbeam/pull/533
- https://github.com/crossbeam-rs/crossbeam
- https://rustsec.org/advisories/RUSTSEC-2020-0052.html
