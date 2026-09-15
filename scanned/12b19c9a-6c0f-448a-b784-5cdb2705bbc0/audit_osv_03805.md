# [M] ALPINE-CVE-2026-5223

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-5223
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-05-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-5223
Type: osv

## Affected
- Alpine:v3.23: `rust` — affected >=0 <1.91.1-r2
- Alpine:v3.24: `rust` — affected >=0 <1.96.0-r0

## Details
Cargo incorrectly handled symlinks inside of crate tarballs downloaded from third-party registries, allowing a malicious crate to override the source code of another crate from the same registry. The severity of the vulnerability is **medium** for users of third-party registries. Users of crates.io are **not affected**, as crates.io forbids uploading crates containing any symlink.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-5223
