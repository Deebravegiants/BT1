# [M] Capstone doesn't check Skipdata length, leading to cs_insn.bytes heap buffer overflow

## Summary
Severity: Medium
Advisory: CVE-2025-67873
Aliases: GHSA-hj6g-v545-v7jg
CVSS: 4.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-67873
Type: osv

## Details
Capstone is a disassembly framework. In versions 6.0.0-Alpha5 and prior, Skipdata length is not bounds-checked, so a user-provided skipdata callback can make cs_disasm/cs_disasm_iter memcpy more than 24 bytes into cs_insn.bytes, causing a heap buffer overflow in the disassembly path. Commit cbef767ab33b82166d263895f24084b75b316df3 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67873.json
- https://github.com/capstone-engine/capstone/security/advisories/GHSA-hj6g-v545-v7jg
- https://nvd.nist.gov/vuln/detail/CVE-2025-67873
- https://github.com/capstone-engine/capstone/commit/cbef767ab33b82166d263895f24084b75b316df3
