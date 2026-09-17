# [M] tar-rs `unpack_in` can chmod arbitrary directories by following symlinks

## Summary
Severity: Medium
Advisory: GHSA-j4xf-2g29-59ph
CVE: CVE-2026-33056
CWE: CWE-61
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-j4xf-2g29-59ph
Type: github-advisory

## Affected
- crates.io: `tar` — affected >=0 <0.4.45

## Details
## Summary

When unpacking a tar archive, the `tar` crate's `unpack_dir` function uses `fs::metadata()` to check whether a path that already exists is a directory. Because `fs::metadata()` follows symbolic links, a crafted tarball containing a symlink entry followed by a directory entry with the same name causes the crate to treat the symlink target as a valid existing directory — and subsequently apply `chmod` to it. This allows an attacker to modify the permissions of arbitrary directories outside the extraction root.

## Reproducer

A malicious tarball contains two entries: (1) a symlink `foo` pointing to an arbitrary external directory, and (2) a directory entry `foo/.` (or just `foo`). When unpacked, `create_dir("foo")` fails with `EEXIST` because the symlink is already on disk. The `fs::metadata()` check then follows the symlink, sees a directory at the target, and allows processing to continue. The directory entry's mode bits are then applied via `chmod`, which also follows the symlink — modifying the permissions of the external target directory.

## Fix 

The fix is very simple, we now use `fs::symlink_metadata()` in `unpack_dir`, so symlinks are detected and rejected rather than followed.

## Credit

This issue was reported by @xokdvium - thank you!

## References
- https://github.com/alexcrichton/tar-rs/security/advisories/GHSA-j4xf-2g29-59ph
- https://nvd.nist.gov/vuln/detail/CVE-2026-33056
- https://github.com/alexcrichton/tar-rs/commit/17b1fd84e632071cb8eef9d3709bf347bd266446
- https://github.com/alexcrichton/tar-rs
- https://rustsec.org/advisories/RUSTSEC-2026-0067.html
