# [H] NSA Ghidra Auto-Analysis Annotation Command Execution

## Summary
Severity: High
Advisory: CVE-2026-4946
Aliases: GHSA-mc3p-mq2p-xw6v
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-29
Source: https://osv.dev/vulnerability/CVE-2026-4946
Type: osv

## Details
Ghidra versions prior to 12.0.3 improperly process annotation directives embedded in automatically extracted binary data, resulting in arbitrary command execution when an analyst interacts with the UI. Specifically, the @execute annotation (which is intended for trusted, user-authored comments) is also parsed in comments generated during auto-analysis (such as CFStrings in Mach-O binaries). This allows a crafted binary to present seemingly benign clickable text which, when clicked, executes attacker-controlled commands on the analyst’s machine.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4946.json
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-mc3p-mq2p-xw6v
- https://nvd.nist.gov/vuln/detail/CVE-2026-4946
- https://takeonme.org/gcves/GCVE-1337-2026-00000000000000000000000000000000000000000000000001011111111111000111111110000000000000000000000000000000000000000000000000000000110
