# [H] libsecp256k1 contains side-channel timing attack

## Summary
Severity: High
Advisory: GHSA-hrjm-c879-pp86
CVE: CVE-2019-25003
CWE: CWE-208
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-hrjm-c879-pp86
Type: github-advisory

## Affected
- crates.io: `libsecp256k1` — affected >=0 <0.3.1

## Details
Versions of libsecp256k1 prior to 0.3.1 did not execute `Scalar::check_overflow` in constant time. This allows an attacker to potentially leak information via a timing attack. The flaw was corrected by modifying `Scalar::check_overflow` to execute in constant time.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25003
- https://github.com/paritytech/libsecp256k1/commit/11ba23a9766a5079918cd9f515bc100bc8164b50
- https://github.com/paritytech/libsecp256k1
- https://rustsec.org/advisories/RUSTSEC-2019-0027.html
