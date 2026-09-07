# [H] axum-core has no default limit put on request bodies

## Summary
Severity: High
Advisory: GHSA-m77f-652q-wwp4
CVE: CVE-2022-3212
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-15
Source: https://github.com/advisories/GHSA-m77f-652q-wwp4
Type: github-advisory

## Affected
- crates.io: `axum-core` — affected >=0 <0.2.8
- crates.io: `axum-core` — affected >=0.3.0-rc.1 <0.3.0-rc.2

## Details
`<bytes::Bytes as axum_core::extract::FromRequest>::from_request` would not, by default, set a limit for the size of the request body. That meant if a malicious peer would send a very large (or infinite) body your server might run out of memory and crash.

This also applies to these extractors which used `Bytes::from_request` internally:
- `axum::extract::Form`
- `axum::extract::Json`
- `String`

The fix is also in `axum-core` `0.3.0.rc.2` but `0.3.0.rc.1` _is_ vulnerable.

Because `axum` depends on `axum-core` it is vulnerable as well. The vulnerable versions of `axum` are `<= 0.5.15` and `0.6.0.rc.1`. `axum` `>= 0.5.16` and `>= 0.6.0.rc.2` does have the fix and are not vulnerable.

The patched versions will set a 2 MB limit by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3212
- https://github.com/tokio-rs/axum/pull/1346
- https://github.com/tokio-rs/axum
- https://rustsec.org/advisories/RUSTSEC-2022-0055.html
