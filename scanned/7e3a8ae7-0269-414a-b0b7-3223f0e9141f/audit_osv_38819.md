# [M] Termix: Command injection in extractArchive/compressFiles via double-quote escaping bypass

## Summary
Severity: Medium
Advisory: CVE-2026-42453
Aliases: GHSA-rvg4-7vvq-9c2w
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42453
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. Prior to version 2.1.0, the extractArchive and compressFiles endpoints in file-manager.ts use double-quoted strings for shell command construction, unlike all other file manager operations which use single-quote escaping. Double quotes allow $(command) substitution, enabling command injection on the remote SSH host. This issue has been patched in version 2.1.0.

## References
- https://github.com/Termix-SSH/Termix/releases/tag/release-2.1.0-tag
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42453.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-rvg4-7vvq-9c2w
- https://nvd.nist.gov/vuln/detail/CVE-2026-42453
