# [M] libreoffice-convert vulnerable to path traversal / arbitrary file write

## Summary
Severity: Medium
Advisory: GHSA-gmxc-r82q-347r
CVE: CVE-2026-54732
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-27
Source: https://github.com/advisories/GHSA-gmxc-r82q-347r
Type: github-advisory

## Affected
- npm: `libreoffice-convert` — affected >=0 <1.8.2

## Details
### Impact
options.fileName is used to build a filesystem path
(path.join(tempDir.name, fileName)) and the caller-supplied document buffer is
written there, but fileName is never reduced to a base name. A fileName containing
"../" escapes the temporary directory, so a caller can write arbitrary content to an
arbitrary path the process can write to (e.g. ~/.ssh/authorized_keys, an /etc/cron.d
entry, or a web root).

### Patches
Version 1.8.2 uses `path.basename` on `filename` to make sure the temp directory can not be escaped.

### Workarounds
Make sure you supply the filename yourself and don't have it user supplied or use `path.basename` on `filename` before using it in `libreoffice-convert`.

## References
- https://github.com/elwerene/libreoffice-convert/security/advisories/GHSA-gmxc-r82q-347r
- https://github.com/elwerene/libreoffice-convert/commit/b78f17df9b9183bd503fc4635fc8b3df6705047b
- https://github.com/elwerene/libreoffice-convert
