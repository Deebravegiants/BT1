# [M] SecureJoin: on windows, paths outside of the rootfs could be inadvertently produced

## Summary
Severity: Medium
Advisory: GHSA-6xv5-86q9-7xr8
Ecosystem: Go
Published: 2023-09-07
Source: https://github.com/advisories/GHSA-6xv5-86q9-7xr8
Type: github-advisory

## Affected
- Go: `github.com/cyphar/filepath-securejoin` — affected >=0 <0.2.4

## Details
### Impact
For Windows users of `github.com/cyphar/filepath-securejoin`, until v0.2.4 it was possible for certain rootfs and path combinations (in particular, where a malicious Unix-style `/`-separated unsafe path was used with a Windows-style rootfs path) to result in generated paths that were outside of the provided rootfs.

It is unclear to what extent this has a practical impact on real users, but given the possible severity of the issue we have released an emergency patch release that resolves this issue.

Thanks to  @pjbgf for discovering, debugging, and fixing this issue (as well as writing some tests for it).

### Patches
c121231e1276e11049547bee5ce68d5a2cfe2d9b is the patch fixing this issue. v0.2.4 contains the fix.

### Workarounds
Users could use `filepath.FromSlash()` on all unsafe paths before passing them to `filepath-securejoin`.

### References
See #9.

## References
- https://github.com/cyphar/filepath-securejoin/security/advisories/GHSA-6xv5-86q9-7xr8
- https://github.com/cyphar/filepath-securejoin/pull/9
- https://github.com/cyphar/filepath-securejoin/commit/c121231e1276e11049547bee5ce68d5a2cfe2d9b
- https://github.com/cyphar/filepath-securejoin
- https://github.com/cyphar/filepath-securejoin/releases/tag/v0.2.4
