# [M] ALPINE-CVE-2026-33056

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-33056
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33056
Type: osv

## Affected
- Alpine:v3.20: `rust` — affected >=0 <1.78.0-r1
- Alpine:v3.21: `rust` — affected >=0 <1.83.0-r1
- Alpine:v3.22: `rust` — affected >=0 <1.87.0-r1
- Alpine:v3.23: `rust` — affected >=0 <1.91.1-r1
- Alpine:v3.24: `rust` — affected >=0 <1.94.0-r1

## Details
tar-rs is a tar archive reading/writing library for Rust. In versions 0.4.44 and below, when unpacking a tar archive, the tar crate's unpack_dir function uses fs::metadata() to check whether a path that already exists is a directory. Because fs::metadata() follows symbolic links, a crafted tarball containing a symlink entry followed by a directory entry with the same name causes the crate to treat the symlink target as a valid existing directory — and subsequently apply chmod to it. This allows an attacker to modify the permissions of arbitrary directories outside the extraction root. This issue has been fixed in version 0.4.45.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33056
