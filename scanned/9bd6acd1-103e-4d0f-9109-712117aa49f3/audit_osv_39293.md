# [M] RustFS: Hard-coded RSA private key in license verifier permits arbitrary license forgery

## Summary
Severity: Medium
Advisory: CVE-2026-45041
Aliases: GHSA-923g-jp7v-f97f
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-45041
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. Prior to 1.0.0-beta.2, crates/appauth/src/token.rs ships a 2048-bit RSA private key as a string constant named TEST_PRIVATE_KEY and uses it in production via parse_license() to "verify" license tokens. Because the key is embedded in every published source release and binary, anyone who can read the repository or extract it from the binary can mint arbitrary license tokens (any subject, any expiration). When the license Cargo feature is enabled, this defeats the entire license-enforcement mechanism. This vulnerability is fixed in 1.0.0-beta.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45041.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-923g-jp7v-f97f
- https://nvd.nist.gov/vuln/detail/CVE-2026-45041
