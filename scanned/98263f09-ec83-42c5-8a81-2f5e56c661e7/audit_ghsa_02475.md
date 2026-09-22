# [H] Links in archive can create arbitrary directories

## Summary
Severity: High
Advisory: GHSA-62jx-8vmh-4mcw
CVE: CVE-2021-38511
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-62jx-8vmh-4mcw
Type: github-advisory

## Affected
- crates.io: `tar` — affected >=0 <0.4.36

## Details
When unpacking a tarball that contains a symlink the tar crate may create directories outside of the directory it's supposed to unpack into. The function errors when it's trying to create a file, but the folders are already created at this point.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38511
- https://github.com/alexcrichton/tar-rs/issues/238
- https://github.com/alexcrichton/tar-rs/pull/259
- https://github.com/alexcrichton/tar-rs
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/tar/RUSTSEC-2021-0080.md
- https://rustsec.org/advisories/RUSTSEC-2021-0080.html
