# [H] libgit2-sys affected by memory corruption, denial of service, and arbitrary code execution in libgit2

## Summary
Severity: High
Advisory: GHSA-22q8-ghmq-63vf
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-02-12
Source: https://github.com/advisories/GHSA-22q8-ghmq-63vf
Type: github-advisory

## Affected
- crates.io: `libgit2-sys` — affected >=0 <0.16.2

## Details
The [libgit2](https://github.com/libgit2/libgit2/) project fixed three security issues in the 1.7.2 release. These issues are:

* The `git_revparse_single` function can potentially enter an infinite loop on a well-crafted input, potentially causing a Denial of Service. This function is exposed in the `git2` crate via the [`Repository::revparse_single`](https://docs.rs/git2/latest/git2/struct.Repository.html#method.revparse_single) method.
* The `git_index_add` function may cause heap corruption and possibly lead to arbitrary code execution. This function is exposed in the `git2` crate via the [`Index::add`](https://docs.rs/git2/latest/git2/struct.Index.html#method.add) method.
* The smart transport negotiation may experience an out-of-bounds read when a remote server did not advertise capabilities.

The `libgit2-sys` crate bundles libgit2, or optionally links to a system libgit2 library. In either case, versions of the libgit2 library less than 1.7.2 are vulnerable. The 0.16.2 release of `libgit2-sys` bundles the fixed version of 1.7.2, and requires a system libgit2 version of at least 1.7.2.

It is recommended that all users upgrade.

## References
- https://github.com/rust-lang/git2-rs/pull/1017
- https://github.com/rust-lang/git2-rs/commit/9e57876be78924c1e5f3f268bb599e3981fe58bb
- https://github.com/rust-lang/git2-rs
- https://rustsec.org/advisories/RUSTSEC-2024-0013.html
