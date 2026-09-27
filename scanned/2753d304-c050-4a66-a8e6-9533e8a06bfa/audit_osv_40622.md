# [H] rsync < 3.5.0 Arbitrary File Read via Symlink Following

## Summary
Severity: High
Advisory: CVE-2026-53802
Aliases: GHSA-4mfr-8jrv-49x4
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53802
Type: osv

## Details
rsync before 3.5.0 contains an arbitrary file read vulnerability that allows attackers to read files accessible to the rsync daemon process by exploiting symlink following in input configuration file handling including --files-from, --password-file, and filter merge files. Attackers can place a symlink at a predictable --files-from or --password-file path, or supply a --files-from path that escapes the daemon module root, to read arbitrary files accessible to the rsync process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53802.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-4mfr-8jrv-49x4
- https://nvd.nist.gov/vuln/detail/CVE-2026-53802
- https://www.vulncheck.com/advisories/rsync-arbitrary-file-read-via-symlink-following
- https://github.com/RsyncProject/rsync
