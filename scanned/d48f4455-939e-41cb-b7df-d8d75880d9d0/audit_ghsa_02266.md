# [H] Improper Certificate Validation in openssl

## Summary
Severity: High
Advisory: GHSA-34p9-f4q3-c4r7
CVE: CVE-2016-10931
CWE: CWE-295
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-34p9-f4q3-c4r7
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0 <0.9.0

## Details
All versions of rust-openssl prior to 0.9.0 contained numerous insecure defaults including off-by-default certificate verification and no API to perform hostname verification. Unless configured correctly by a developer, these defaults could allow an attacker to perform man-in-the-middle attacks. The problem was addressed in newer versions by enabling certificate verification by default and exposing APIs to perform hostname verification. Use the SslConnector and SslAcceptor types to take advantage of these new features (as opposed to the lower-level SslContext type).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10931
- https://github.com/sfackler/rust-openssl
- https://github.com/sfackler/rust-openssl/releases/tag/v0.9.0
- https://rustsec.org/advisories/RUSTSEC-2016-0001.html
