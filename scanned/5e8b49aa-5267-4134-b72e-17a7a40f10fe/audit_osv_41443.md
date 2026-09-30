# [H] CVE-2026-6069

## Summary
Severity: High
Advisory: CVE-2026-6069
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-6069
Type: osv

## Details
NASM’s disasm() function contains a stack based buffer overflow when formatting disassembly output, allowing an attacker triggered out-of-bounds write when `slen` exceeds the buffer capacity.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6069.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6069
- https://github.com/netwide-assembler/nasm/issues/217
