# [H] Uncontrolled Resource Consumption in simple_asn1

## Summary
Severity: High
Advisory: GHSA-g4h2-4wvh-grc5
CVE: CVE-2021-45711
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-g4h2-4wvh-grc5
Type: github-advisory

## Affected
- crates.io: `simple_asn1` — affected >=0.6.0 <0.6.1

## Details
An issue was discovered in the simple_asn1 crate 0.6.0 before 0.6.1 for Rust. There is a panic if UTCTime data, supplied by a remote attacker, has a second character greater than 0x7f.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45711
- https://github.com/acw/simple_asn1/issues/27
- https://github.com/acw/simple_asn1/commit/d7d39d709577710e9dc8833ee57d200eef366db8
- https://github.com/acw/simple_asn1
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/simple_asn1/RUSTSEC-2021-0125.md
- https://rustsec.org/advisories/RUSTSEC-2021-0125.html
