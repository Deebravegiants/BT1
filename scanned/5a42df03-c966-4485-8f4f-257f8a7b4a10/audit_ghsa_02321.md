# [H] os_str_bytes relies on undefined behavior of `char::from_u32_unchecked`

## Summary
Severity: High
Advisory: GHSA-q948-x8rf-888m
CVE: CVE-2020-35865
CWE: CWE-704
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-q948-x8rf-888m
Type: github-advisory

## Affected
- crates.io: `os_str_bytes` — affected >=0 <2.0.0

## Details
The Windows implementation of this crate relied on the behavior of std::char::from_u32_unchecked when its safety clause is violated. Even though this worked with Rust versions up to 1.42 (at least), that behavior could change with any new Rust version, possibly leading a security issue.

The flaw was corrected in version 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35865
- https://github.com/dylni/os_str_bytes/pull/1
- https://github.com/dylni/os_str_bytes
- https://rustsec.org/advisories/RUSTSEC-2020-0012.html
