# [H] ALPINE-CVE-2021-37713

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-37713
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2021-08-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-37713
Type: osv

## Affected
- Alpine:v3.11: `nodejs` — affected >=0 <12.22.6-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.22.6-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.15: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.16: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.17: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.18: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.19: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.20: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.21: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.22: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.23: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.24: `nodejs` — affected >=0 <14.17.6-r0

## Details
The npm package "tar" (aka node-tar) before versions 4.4.18, 5.0.10, and 6.1.9 has an arbitrary file creation/overwrite and arbitrary code execution vulnerability. node-tar aims to guarantee that any file whose location would be outside of the extraction target directory is not extracted. This is, in part, accomplished by sanitizing absolute paths of entries within the archive, skipping archive entries that contain `..` path portions, and resolving the sanitized paths against the extraction target directory. This logic was insufficient on Windows systems when extracting tar files that contained a path that was not an absolute path, but specified a drive letter different from the extraction target, such as `C:some\path`. If the drive letter does not match the extraction target, for example `D:\extraction\dir`, then the result of `path.resolve(extractionDirectory, entryPath)` would resolve against the current working directory on the `C:` drive, rather than the extraction target directory. Additionally, a `..` portion of the path could occur immediately after the drive letter, such as `C:../foo`, and was not properly sanitized by the logic that checked for `..` within the normalized and split portions of the path. This only affects users of `node-tar` on Windows systems. These issues were addressed in releases 4.4.18, 5.0.10 and 6.1.9. The v3 branch of node-tar has been deprecated and did not receive patches for these issues. If you are still using a v3 release we recommend you update to a more recent version of node-tar. There is no reasonable way to work around this issue without performing the same path normalization procedures that node-tar now does. Users are encouraged to upgrade to the latest patched versions of node-tar, rather than attempt to sanitize paths themselves.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-37713
