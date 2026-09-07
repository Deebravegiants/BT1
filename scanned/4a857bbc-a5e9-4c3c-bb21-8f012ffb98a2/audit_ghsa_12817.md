# [M] git2-rs fails to verify SSH keys by default

## Summary
Severity: Medium
Advisory: GHSA-m4ch-rfv5-x5g3
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-m4ch-rfv5-x5g3
Type: github-advisory

## Affected
- crates.io: `libgit2-sys` — affected >=0.14.0 <0.14.2
- crates.io: `libgit2-sys` — affected >=0 <0.13.5
- crates.io: `git2` — affected >=0 <0.16.1

## Details
The git2 and libgit2-sys crates are Rust wrappers around the [libgit2](https://libgit2.org/) C library. It was discovered that libgit2 1.5.0 and below did not verify SSH host keys when establishing an SSH connection, exposing users of the library to Man-In-the-Middle attacks.

The libgit2 team assigned [CVE-2023-22742](https://github.com/libgit2/libgit2/security/advisories/GHSA-8643-3wh5-rmjq) to this vulnerability. The following versions of the libgit2-sys Rust crate have been released:

* libgit2-sys 0.14.2, updating the underlying libgit2 C library to version 1.5.1.
* libgit2-sys 0.13.5, updating the underlying libgit2 C library to version 1.4.5.

A new git2 crate version has also been released, 0.16.1. This version only bumps its libgit2-sys dependency to ensure no vulnerable libgit2-sys versions are used, but contains no code changes: if you update the libgit2-sys version there is no need to also update the git2 crate version.

[You can learn more about this vulnerability in libgit2's advisory](https://github.com/libgit2/libgit2/security/advisories/GHSA-8643-3wh5-rmjq)

## References
- https://github.com/libgit2/libgit2/security/advisories/GHSA-8643-3wh5-rmjq
- https://github.com/rust-lang/git2-rs/security/advisories/GHSA-m4ch-rfv5-x5g3
- https://nvd.nist.gov/vuln/detail/CVE-2023-22742
- https://github.com/rust-lang/git2-rs/commit/87934f87d36753ed702792ec063be7246444a8e1
- https://github.com/rust-lang/git2-rs
- https://rustsec.org/advisories/RUSTSEC-2023-0003.html
