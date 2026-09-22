# [M] Capstone SH disassembler `sh_disassemble` out-of-bounds read via crafted SH2A bytecode

## Summary
Severity: Medium
Advisory: CVE-2026-55894
Aliases: GHSA-gf2c-xwcp-hvf4
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-55894
Type: osv

## Details
Capstone is a disassembly framework. In 6.0.0-Alpha9 and earlier, Capstone's arch/SH/SHDisassembler.c sh_disassemble() function computes an idx value from a raw 16-bit instruction without ensuring it is within the active mode-specific decode[] function-pointer table. An application using CS_ARCH_SH with CS_MODE_SH2A or CS_MODE_SH4A and CS_MODE_SHFPU can pass crafted bytecode through cs_disasm_iter() or cs_disasm(), causing the decode[idx] test to read outside the table and terminate the process with a segmentation fault. No code execution or information disclosure was demonstrated. This issue is fixed in version 6.0.0-Alpha10.

## References
- https://github.com/capstone-engine/capstone/releases/tag/6.0.0-Alpha10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55894.json
- https://github.com/capstone-engine/capstone/security/advisories/GHSA-gf2c-xwcp-hvf4
- https://nvd.nist.gov/vuln/detail/CVE-2026-55894
- https://github.com/capstone-engine/capstone/commit/09e76802380b9e94d9720c44458d9d5282219e7e
- https://github.com/capstone-engine/capstone/commit/e17ee44a8307ea33375b4727ac4f987650bf7bed
- https://github.com/capstone-engine/capstone/pull/2968
- https://github.com/capstone-engine/capstone/pull/2969
