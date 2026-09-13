# [H] rust-openssl has undefined behavior in X509Ref::ocsp_responders for certificates with non-UTF-8 OCSP URLs

## Summary
Severity: High
Advisory: GHSA-xp3w-r5p5-63rr
CVE: CVE-2026-42327
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-xp3w-r5p5-63rr
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.9.7 <0.10.79

## Details
`X509Ref::ocsp_responders` returns OCSP responder URLs from a certificate's AIA extension as `OpensslString`, whose `Deref<Target = str>` wraps the raw bytes with `str::from_utf8_unchecked`. OpenSSL does not enforce that the underlying IA5String is ASCII, so a certificate with non-UTF-8 bytes in its OCSP accessLocation causes safe Rust code to construct a `&str` that violates the UTF-8 invariant — resulting in undefined behavior.

## References
- https://github.com/rust-openssl/rust-openssl/security/advisories/GHSA-xp3w-r5p5-63rr
- https://nvd.nist.gov/vuln/detail/CVE-2026-42327
- https://github.com/rust-openssl/rust-openssl
