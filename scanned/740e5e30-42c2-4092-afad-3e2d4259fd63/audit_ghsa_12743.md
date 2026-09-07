# [H] Warp vulnerable to Path Traversal via Improper validation of Windows paths

## Summary
Severity: High
Advisory: GHSA-8v4j-7jgf-5rg9
CWE: CWE-22
Ecosystem: crates.io
Published: 2023-01-31
Source: https://github.com/advisories/GHSA-8v4j-7jgf-5rg9
Type: github-advisory

## Affected
- crates.io: `warp` — affected >=0 <0.3.3

## Details
Path resolution in `warp::filters::fs::dir` didn't correctly validate Windows paths meaning paths like `/foo/bar/c:/windows/web/screen/img101.png` would be allowed and respond with the contents of `c:/windows/web/screen/img101.png`. Thus users could potentially read files anywhere on the filesystem.

This only impacts Windows. Linux and other unix likes are not impacted by this.

## References
- https://github.com/seanmonstar/warp/issues/937
- https://github.com/seanmonstar/warp/pull/997
- https://github.com/seanmonstar/warp/commit/0074a0a3e98786509259bfe3821d3b3f094257aa
- https://github.com/seanmonstar/warp
- https://rustsec.org/advisories/RUSTSEC-2022-0082.html
