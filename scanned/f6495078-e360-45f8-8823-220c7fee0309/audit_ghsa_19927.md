# [M] hyper-staticfile's improper validation of Windows paths could lead to directory traversal attack

## Summary
Severity: Medium
Advisory: GHSA-7p7c-pvvx-2vx3
CWE: CWE-22
Ecosystem: crates.io
Published: 2022-12-05
Source: https://github.com/advisories/GHSA-7p7c-pvvx-2vx3
Type: github-advisory

## Affected
- crates.io: `hyper-staticfile` — affected >=0 <0.9.2
- crates.io: `hyper-staticfile` — affected >=0.10.0-alpha.1 <0.10.0-alpha.2

## Details
Path resolution in `hyper-staticfile` didn't correctly validate Windows paths, meaning paths like `/foo/bar/c:/windows/web/screen/img101.png` would be allowed and respond with the contents of `c:/windows/web/screen/img101.png`. Thus users could potentially read files anywhere on the filesystem.

This only impacts Windows. Linux and other unix likes are not impacted by this.

## References
- https://github.com/stephank/hyper-staticfile/issues/35
- https://github.com/stephank/hyper-staticfile/pull/36
- https://github.com/stephank/hyper-staticfile/commit/1e40e31d64bc6b32e595d24074092dcf84410b2b
- https://github.com/stephank/hyper-staticfile
- https://rustsec.org/advisories/RUSTSEC-2022-0069.html
