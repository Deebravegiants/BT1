# [C] Type confusion if __private_get_type_id__ is overriden

## Summary
Severity: Critical
Advisory: GHSA-jq66-xh47-j9f3
CVE: CVE-2020-25575
CWE: CWE-843
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-jq66-xh47-j9f3
Type: github-advisory

## Affected
- crates.io: `failure` — affected >=0

## Details
An issue was discovered in the failure crate through 0.1.5 for Rust. It may introduce "compatibility hazards" in some applications, and has a type confusion flaw when downcasting. NOTE: This vulnerability only affects products that are no longer supported by the maintainer. NOTE: This may overlap CVE-2019-25010.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25575
- https://github.com/rust-lang-nursery/failure/issues/336
- https://github.com/RustCrypto/hashes/pull/91
- https://boats.gitlab.io/blog/post/failure-to-fehler
- https://github.com/RustSec/advisory-db/blob/main/crates/failure/RUSTSEC-2019-0036.md
- https://rustsec.org/advisories/RUSTSEC-2019-0036.html
- https://rustsec.org/advisories/RUSTSEC-2020-0036.html
