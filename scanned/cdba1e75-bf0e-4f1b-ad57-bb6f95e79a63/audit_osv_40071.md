# [M] Capstone M68K and RISCV `cs_insn_name()` invalid IDs can trigger out-of-bounds reads and process crashes

## Summary
Severity: Medium
Advisory: CVE-2026-49282
Aliases: GHSA-jrw4-wj52-2vw8
CVSS: 5.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-49282
Type: osv

## Details
Capstone is a disassembly framework. Prior to version 6.0.0-Alpha9, Capstone's public `cs_insn_name()` API forwards caller-supplied instruction IDs directly to the selected architecture backend. Most backends validate the ID before indexing instruction-name tables, but the M68K and RISCV backends have missing or incomplete bounds checks. On a Capstone handle opened for M68K or RISCV, a caller-controlled invalid instruction ID can trigger an out-of-bounds read and crash the process. The demonstrated impact is availability loss in applications or bindings that expose instruction-name lookup to untrusted IDs. No code execution or data disclosure was demonstrated. Version 6.0.0-Alpha9 patches the issue.

## References
- https://github.com/capstone-engine/capstone/blob/251c5bb4bc9bb92973e738ae3c5f4ef86f103356/ChangeLog#L102
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49282.json
- https://github.com/capstone-engine/capstone/security/advisories/GHSA-jrw4-wj52-2vw8
- https://nvd.nist.gov/vuln/detail/CVE-2026-49282
