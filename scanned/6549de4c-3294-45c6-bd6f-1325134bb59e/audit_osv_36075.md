# [H] extract-zip arbitrary file write outside the destination directory via a symlink at the final path component

## Summary
Severity: High
Advisory: CVE-2026-19693
Aliases: GHSA-7pqw-9j4j-h8q3
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-19693
Type: osv

## Details
extract-zip through 2.0.1 containment-checks only the parent directory of each archive entry and never the entry's own final path component, so an archive containing two entries with identical names - a symlink whose target is outside the destination, followed by a regular file - writes through the planted symlink and yields an arbitrary file write outside the destination directory.

## References
- https://www.npmjs.com/package/extract-zip
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19693.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19693
- https://github.com/max-mapper/extract-zip
