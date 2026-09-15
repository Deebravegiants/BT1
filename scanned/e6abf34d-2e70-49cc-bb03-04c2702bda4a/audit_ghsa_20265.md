# [M] tower-http's improper validation of Windows paths could lead to directory traversal attack

## Summary
Severity: Medium
Advisory: GHSA-wwh2-r387-g5rm
CWE: CWE-22
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-wwh2-r387-g5rm
Type: github-advisory

## Affected
- crates.io: `tower-http` — affected >=0.2.0 <0.2.1
- crates.io: `tower-http` — affected >=0 <0.1.3

## Details
`tower_http::services::fs::ServeDir` didn't correctly validate Windows paths meaning paths like `/foo/bar/c:/windows/web/screen/img101.png` would be allowed and respond with the contents of `c:/windows/web/screen/img101.png`. Thus users could potentially read files anywhere on the filesystem. This only impacts Windows. Linux and other unix likes are not impacted by this.

## References
- https://github.com/tower-rs/tower-http/pull/204
- https://github.com/tower-rs/tower-http
- https://rustsec.org/advisories/RUSTSEC-2021-0135.html
