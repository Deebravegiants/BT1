# [C] rsync < 3.5.0 Symlink Following Arbitrary File Overwrite

## Summary
Severity: Critical
Advisory: CVE-2026-53803
Aliases: GHSA-g9f4-7q66-9582
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53803
Type: osv

## Details
rsync before 3.5.0 contains a symlink following vulnerability that allows local attackers to overwrite arbitrary files by placing a symlink at a predictable output path such as --log-file, --write-batch, or daemon-mode log and statistics paths. Attackers can exploit rsync's failure to reject symlinks during ancillary file writes to redirect output to arbitrary filesystem locations, achieving local privilege escalation on installations where rsync runs with elevated privileges such as setuid or privileged daemon configurations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53803.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-g9f4-7q66-9582
- https://nvd.nist.gov/vuln/detail/CVE-2026-53803
- https://www.vulncheck.com/advisories/rsync-symlink-following-arbitrary-file-overwrite
- https://github.com/RsyncProject/rsync
