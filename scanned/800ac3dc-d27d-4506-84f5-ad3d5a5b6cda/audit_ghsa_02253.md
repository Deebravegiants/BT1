# [M] Data races in reffers

## Summary
Severity: Medium
Advisory: GHSA-39xg-8p43-h76x
CVE: CVE-2020-36203
CWE: CWE-362, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-39xg-8p43-h76x
Type: github-advisory

## Affected
- crates.io: `reffers` — affected >=0 <0.6.1

## Details
ARefss<'a, V> is a type that is assumed to contain objects that are Send + Sync.

In the affected versions of this crate, Send/Sync traits are unconditionally implemented for ARefss<'a, V>.

By using the ARefss::map() API, we can insert a !Send or !Sync object into ARefss<'a, V>. After that, it is possible to create a data race to the inner object of ARefss<'a, V>, which can lead to undefined behavior & memory corruption.

The flaw was corrected in commit `6dd7ca0` by adding trait bound V: Send + Sync to ARefss::map() API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36203
- https://github.com/diwic/reffers-rs/issues/7
- https://github.com/diwic/reffers-rs/commit/6dd7ca0d50f2464df708975cdafcfaeeb6d41c66
- https://github.com/diwic/reffers-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0094.html
