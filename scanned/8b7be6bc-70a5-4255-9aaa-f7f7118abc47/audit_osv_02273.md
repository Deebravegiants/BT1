# [H] ALPINE-CVE-2021-37712

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-37712
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2021-08-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-37712
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
The npm package "tar" (aka node-tar) before versions 4.4.18, 5.0.10, and 6.1.9 has an arbitrary file creation/overwrite and arbitrary code execution vulnerability. node-tar aims to guarantee that any file whose location would be modified by a symbolic link is not extracted. This is, in part, achieved by ensuring that extracted directories are not symlinks. Additionally, in order to prevent unnecessary stat calls to determine whether a given path is a directory, paths are cached when directories are created. This logic was insufficient when extracting tar files that contained both a directory and a symlink with names containing unicode values that normalized to the same value. Additionally, on Windows systems, long path portions would resolve to the same file system entities as their 8.3 "short path" counterparts. A specially crafted tar archive could thus include a directory with one form of the path, followed by a symbolic link with a different string that resolves to the same file system entity, followed by a file using the first form. By first creating a directory, and then replacing that directory with a symlink that had a different apparent name that resolved to the same entry in the filesystem, it was thus possible to bypass node-tar symlink checks on directories, essentially allowing an untrusted tar file to symlink into an arbitrary location and subsequently extracting arbitrary files into that location, thus allowing arbitrary file creation and overwrite. These issues were addressed in releases 4.4.18, 5.0.10 and 6.1.9. The v3 branch of node-tar has been deprecated and did not receive patches for these issues. If you are still using a v3 release we recommend you update to a more recent version of node-tar. If this is not possible, a workaround is available in the referenced GHSA-qq89-hq3f-393p.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-37712
