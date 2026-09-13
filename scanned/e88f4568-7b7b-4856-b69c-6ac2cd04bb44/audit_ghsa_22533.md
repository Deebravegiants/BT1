# [M] Observable Timing Discrepancy in totp-rs

## Summary
Severity: Medium
Advisory: GHSA-8vxv-2g8p-2249
CVE: CVE-2022-29185
CWE: CWE-203, CWE-208
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8vxv-2g8p-2249
Type: github-advisory

## Affected
- crates.io: `totp-rs` — affected >=0 <1.1.0

## Details
### Impact
Token comparison was not constant time, and could theorically be used to guess value of an TOTP token, and thus reuse it in the same time window. The attacker would have to know the password beforehand nonetheless.

### Patches
Library now used constant-time comparison.

### Workarounds
No.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [totp-rs](https://github.com/constantoine/totp-rs)
* Email us at [cleo.rebert@gmail.com](mailto:cleo.rebert@gmail.com)

## References
- https://github.com/constantoine/totp-rs/security/advisories/GHSA-8vxv-2g8p-2249
- https://nvd.nist.gov/vuln/detail/CVE-2022-29185
- https://github.com/constantoine/totp-rs/issues/13
- https://github.com/constantoine/totp-rs/commit/1f1e1a6fe722deb1656f483b1367ea4be978db5b
- https://github.com/constantoine/totp-rs
- https://github.com/constantoine/totp-rs/compare/v1.0...v1.1.0
- https://github.com/constantoine/totp-rs/releases/tag/v1.1.0
- https://rustsec.org/advisories/RUSTSEC-2022-0018.html
