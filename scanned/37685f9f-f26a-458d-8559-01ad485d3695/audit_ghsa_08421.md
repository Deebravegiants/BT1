# [H] apko dirFS has a symlink-following path traversal that allows multiple entry points to escape the build root

## Summary
Severity: High
Advisory: GHSA-qq3r-w4hj-gjp6
CVE: CVE-2026-42574
CWE: CWE-22, CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-qq3r-w4hj-gjp6
Type: github-advisory

## Affected
- Go: `chainguard.dev/apko` — affected >=0.14.8 <1.2.5

## Details
### Impact

A crafted `.apk` could install a `TypeSymlink` tar entry whose target pointed outside the build root, and a subsequent directory-creation or file-write entry in the same or later archive could traverse that symlink to reach host paths the build user could write to. The root cause was the `sanitizePath` helper in `pkg/apk/fs/rwosfs.go`, which rejected only lexical `..` traversal and did not resolve or refuse symlinks. Every disk-backed `DirFS` method that handed its caller-supplied path to a symlink-following stdlib call — `ReadFile`, `WriteFile`, `Chmod`, `Chown`, `Chtimes`, `MkdirAll`, `Mkdir`, and `Mknod` — was affected. The reachable primitive from a malicious APK during tar extraction is the `MkdirAll` / `Mkdir` / `WriteFile` chain via `apko build-cpio` and disk-backed consumers such as `melange`; the remaining sinks are reachable by direct callers of the `pkg/apk/fs` package. The in-memory `tarfs` install path used by `apko build`, `apko publish`, and `apko build-minirootfs` is not affected.

### Patches

Fixed in apko **v1.2.5** by [#2187](https://github.com/chainguard-dev/apko/pull/2187) / commit [f5a96e1](https://github.com/chainguard-dev/apko/commit/f5a96e1299ac81c7ea9441705ec467688086f442), which scopes all `DirFS` operations through a Go 1.24 `*os.Root`. The `sanitizePath` helper has been removed; `*os.Root` refuses traversal via `..`, absolute-target symlinks, relative-target symlinks, and hardlinks by construction. Regression tests in `pkg/apk/apk/path_traversal_test.go` cover each composite primitive.

### Workarounds

No complete workaround. Operators running pre-1.2.5 apko (or downstream tools such as melange that embed pre-1.2.5 `pkg/apk/fs`) should upgrade. Consuming only APKs from trusted, signed sources reduces but does not eliminate exposure.

### Resources

- https://github.com/chainguard-dev/apko/pull/2187
- https://github.com/chainguard-dev/apko/commit/f5a96e1299ac81c7ea9441705ec467688086f442
- https://github.com/chainguard-dev/apko/releases/tag/v1.2.5
- Related: GHSA-5g94-c2wx-8pxw (CVE-2026-25121) — prior lexical `..` traversal fix

### Credits

apko thanks Oleh Konko ([@1seal](https://github.com/1seal) from [1seal.org](https://1seal.org/)) for the initial report of the symlink-escape class, and to [@Xh081iX](https://github.com/Xh081iX) for a follow-up set of reports covering additional reachable primitives (`ReadFile`, `Chmod`/`Chown`, `Mknod`, `MkdirAll`/`Mkdir`) that shaped the comprehensive fix.

## References
- https://github.com/chainguard-dev/apko/security/advisories/GHSA-qq3r-w4hj-gjp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-42574
- https://github.com/chainguard-dev/apko/pull/2187
- https://github.com/chainguard-dev/apko/commit/f5a96e1299ac81c7ea9441705ec467688086f442
- https://github.com/chainguard-dev/apko
- https://github.com/chainguard-dev/apko/releases/tag/v1.2.5
