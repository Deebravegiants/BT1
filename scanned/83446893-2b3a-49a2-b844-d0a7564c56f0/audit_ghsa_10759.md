# [H] rust-openssl has incorrect bounds assertion in aes key wrap

## Summary
Severity: High
Advisory: GHSA-8c75-8mhr-p7r9
CVE: CVE-2026-41678
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-8c75-8mhr-p7r9
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.10.24 <0.10.78

## Details
### Summary
``aes::unwrap_key()`` has an incorrect bounds assertion on the out buffer size, which can lead to out-of-bounds write.

### Details
``aes::unwrap_key()`` contains an incorrect assertion: it checks that `out.len() + 8 <= in_.len()`, but this condition is reversed. The intended invariant is `out.len() >= in_.len() - 8`, ensuring the output buffer is large enough.

Because of the inverted check, the function only accepts buffers at or below the minimum required size and rejects larger ones. If a smaller buffer is provided the function will write past the end of `out` by `in_.len() - 8 - out.len()` bytes, causing an out-of-bounds write from a safe public function.

### Impact
Vulnerable applications using AES keywrap and allowing attacker controlled buffer sizes could have an attacker trigger an out-of-bounds write.

## References
- https://github.com/rust-openssl/rust-openssl/security/advisories/GHSA-8c75-8mhr-p7r9
- https://nvd.nist.gov/vuln/detail/CVE-2026-41678
- https://github.com/rust-openssl/rust-openssl/pull/2604
- https://github.com/rust-openssl/rust-openssl/commit/718d07ff8ff7be417d5b7a6a0047f1607520b3b6
- https://github.com/rust-openssl/rust-openssl
- https://github.com/rust-openssl/rust-openssl/releases/tag/openssl-v0.10.78
