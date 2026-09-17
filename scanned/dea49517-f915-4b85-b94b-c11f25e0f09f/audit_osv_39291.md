# [C] Tabby: Dragging and Dropping a File into Tabby Can Lead to Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-45038
Aliases: GHSA-m937-jm93-pfp6
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-45038
Type: osv

## Details
Tabby (formerly Terminus) is a highly configurable terminal emulator. Prior to 1.0.233, since Tabby does not escape control characters from file paths when dragging and dropping a file into it, code execution can be achieved. This vulnerability is fixed in 1.0.233.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45038.json
- https://github.com/Eugeny/tabby/security/advisories/GHSA-m937-jm93-pfp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45038
