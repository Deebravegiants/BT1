# [M] ordered_float:NotNan may contain NaN after panic in assignment operators

## Summary
Severity: Medium
Advisory: GHSA-566x-hhrf-qf8m
CVE: CVE-2020-35923
CWE: CWE-460
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-566x-hhrf-qf8m
Type: github-advisory

## Affected
- crates.io: `ordered-float` — affected >=2.0.0 <2.0.1
- crates.io: `ordered-float` — affected >=0.2.2 <1.1.1

## Details
After using an assignment operators such as NotNan::add_assign, NotNan::mul_assign, etc., it was possible for the resulting NotNan value to contain a NaN. This could cause undefined behavior in safe code, because the safe NotNan::cmp method contains internal unsafe code that assumes the value is never NaN. (It could also cause undefined behavior in third-party unsafe code that makes the same assumption, as well as logic errors in safe code.)

This was mitigated starting in version 0.4.0, by panicking if the assigned value is NaN. However, in affected versions from 0.4.0 onward, code that uses the NotNan value during unwinding, or that continues after catching the panic, could still observe the invalid value and trigger undefined behavior.

The flaw is fully corrected in versions 1.1.1 and 2.0.1, by ensuring that the assignment operators panic without modifying the operand, if the result would be NaN.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35923
- https://github.com/reem/rust-ordered-float/pull/71
- https://github.com/reem/rust-ordered-float/commit/c55cda301c943270b7eb2b4765bedbcce56edb90
- https://github.com/reem/rust-ordered-float/commit/da4a8dd49300740a434c095a9c4b408d2415cc08
- https://github.com/reem/rust-ordered-float
- https://rustsec.org/advisories/RUSTSEC-2020-0082.html
