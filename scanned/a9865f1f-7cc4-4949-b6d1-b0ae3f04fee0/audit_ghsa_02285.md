# [M] Incorrect buffer size in crossbeam-channel

## Summary
Severity: Medium
Advisory: GHSA-m8h8-v6jh-c762
CVE: CVE-2020-35904
CWE: CWE-131
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-m8h8-v6jh-c762
Type: github-advisory

## Affected
- crates.io: `crossbeam-channel` — affected >=0.4.3 <0.4.4

## Details
The affected version of this crate's the bounded channel incorrectly assumes that Vec::from_iter has allocated capacity that same as the number of iterator elements. Vec::from_iter does not actually guarantee that and may allocate extra memory. The destructor of the bounded channel reconstructs Vec from the raw pointer based on the incorrect assumes described above. This is unsound and causing deallocation with the incorrect capacity when Vec::from_iter has allocated different sizes with the number of iterator elements.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35904
- https://github.com/crossbeam-rs/crossbeam/pull/533
- https://github.com/crossbeam-rs/crossbeam
- https://rustsec.org/advisories/RUSTSEC-2020-0052.html
