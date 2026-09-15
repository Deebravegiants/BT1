# [H] LiME through 1.12.0 Arbitrary File Overwrite via Symlink Following

## Summary
Severity: High
Advisory: CVE-2026-85092
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85092
Type: osv

## Details
LiME through 1.12.0 fails to validate the disk acquisition output path and does not use O_NOFOLLOW when opening the operator-supplied path parameter, allowing unprivileged local users to overwrite arbitrary root-owned files. An attacker who controls the output directory can create a symbolic link with the expected filename pointing to any root-owned file, and when the acquisition runs in kernel context, LiME follows the link and truncates the target file with the memory acquisition stream.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85092.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85092
- https://www.vulncheck.com/advisories/lime-through-1.12.0-arbitrary-file-overwrite-via-symlink-following
- https://github.com/jtsylve/LiME
- https://github.com/jtsylve/LiME/blob/v1.12.0/src/disk.c#L63
- https://gist.github.com/thesmartshadow/5355949144749b431da41490b63598f5
