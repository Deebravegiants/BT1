# [H] Syncthing vulnerable to symlink traversal and arbitrary file overwrite

## Summary
Severity: High
Advisory: GHSA-28xp-g7f6-7mhf
CVE: CVE-2017-1000420
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-28xp-g7f6-7mhf
Type: github-advisory

## Affected
- Go: `github.com/syncthing/syncthing` — affected >=0

## Details
Syncthing version 0.14.33 and older erronously versions symlinks when they are deleted. If a directory is then created with the same name, a file created in that directory, and the file deleted, it is moved into the symlink target. This can lead to symlink traversal resulting in arbitrary file overwrite.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000420
- https://github.com/syncthing/syncthing/issues/4286
- https://github.com/syncthing/syncthing/commit/f1f21bf22020d9b881478c2e942ba6943c8da2f3
- https://github.com/syncthing/syncthing
