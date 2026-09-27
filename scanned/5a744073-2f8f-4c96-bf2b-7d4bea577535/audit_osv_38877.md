# [M] Tookie: Arbitrary file write via path traversal in -u username / -U userfile output filename

## Summary
Severity: Medium
Advisory: CVE-2026-42866
Aliases: GHSA-rp68-wfv6-3cq3
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-42866
Type: osv

## Details
Tookie is a advanced OSINT information gathering tool. Prior to 4.1fix, modules/modules.py's write_txt, write_csv, write_json, and (commented-but-shipping) scan_file helpers open their output as open(f"{user}.<ext>"), where user comes unsanitized from the -u CLI flag or any line of a -U usernames file. A username that contains path-separator sequences (.., /, \, or an absolute path) causes tookie-osint to write the scan output to an arbitrary path the invoking user has write permission for. This vulnerability is fixed in 4.1fix.

## References
- https://github.com/Alfredredbird/tookie-osint/security/advisories/GHSA-rp68-wfv6-3cq3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42866.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42866
