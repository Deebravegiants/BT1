# [H] CVE-2026-41015

## Summary
Severity: High
Advisory: CVE-2026-41015
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-41015
Type: osv

## Details
radare2 before 9236f44, when configured on UNIX without SSL, allows command injection via a PDB name to rabin2 -PP. NOTE: although users are supposed to use the latest version from git (not a release), the date range for the vulnerable code was less than a week, occurring after 6.1.2 but before 6.1.3.

## References
- https://github.com/radareorg/radare2/blob/9236f44a28812fe911814e1b3a7bcf1e4de5d3c2/SECURITY.md?plain=1#L3-L5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41015.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41015
- https://github.com/radareorg/radare2/issues/25650
- https://github.com/radareorg/radare2/commit/9236f44a28812fe911814e1b3a7bcf1e4de5d3c2
- https://github.com/radareorg/radare2/pull/25651
