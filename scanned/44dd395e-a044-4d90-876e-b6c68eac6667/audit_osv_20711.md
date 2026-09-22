# [H] CVE-2021-36376

## Summary
Severity: High
Advisory: CVE-2021-36376
Aliases: GHSA-5xg3-j2j6-rcx4, RUSTSEC-2021-0105
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-13
Source: https://osv.dev/vulnerability/CVE-2021-36376
Type: osv

## Details
dandavison delta before 0.8.3 on Windows resolves an executable's pathname as a relative path from the current directory.

## References
- https://github.com/dandavison/delta/releases/tag/0.8.3
- https://vuln.ryotak.me/advisories/54
- https://github.com/dandavison/delta/commit/f01846bd443aaf92fdd5ac20f461beac3f6ee3fd
