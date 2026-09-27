# [H] rsync < 3.5.0 TOCTOU Race Condition via Destination Directory Handling

## Summary
Severity: High
Advisory: CVE-2026-53796
Aliases: GHSA-w75h-ccff-w53m
CVSS: 7.5 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53796
Type: osv

## Details
rsync before 3.5.0 contains a time-of-check to time-of-use (TOCTOU) race condition vulnerability in the non-daemon receiver's destination directory handling that allows an attacker who can manipulate destination path parent components to redirect file writes to unintended locations. Attackers can substitute a symlink for a component of the destination path between the path resolution and chdir() call, causing the receiver's working directory to be established outside the intended destination tree so that subsequent relative-path file writes land in unintended filesystem locations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53796.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-w75h-ccff-w53m
- https://nvd.nist.gov/vuln/detail/CVE-2026-53796
- https://www.vulncheck.com/advisories/rsync-toctou-race-condition-via-destination-directory-handling
- https://github.com/RsyncProject/rsync
