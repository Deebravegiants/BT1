# [C] Capstone SH disassembler `set_reg_n` heap buffer overflow via crafted SH2A FPU bytecode

## Summary
Severity: Critical
Advisory: CVE-2026-55893
Aliases: GHSA-3hpv-wr3j-rxwh
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-55893
Type: osv

## Details
Capstone is a disassembly framework. In 6.0.0-Alpha9 and earlier, Capstone's arch/SH/SHDisassembler.c SH floating-point decoders such as opFADD, opFMUL, and opFSUB call set_reg() and set_reg_n() using sh_info.op.op_count without checking the fixed-size operands[] array. Repeated crafted instructions processed through cs_disasm_iter() or cs_disasm() with CS_ARCH_SH, CS_MODE_SH2A or CS_MODE_SH4A, CS_MODE_SHFPU, and CS_OPT_DETAIL can increment the operand count beyond the 176-byte sh_info allocation and perform a four-byte heap buffer overflow write. The corruption can crash the process and may enable code execution depending on heap layout. This issue is fixed in version 6.0.0-Alpha10.

## References
- https://github.com/capstone-engine/capstone/releases/tag/6.0.0-Alpha10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55893.json
- https://github.com/capstone-engine/capstone/security/advisories/GHSA-3hpv-wr3j-rxwh
- https://nvd.nist.gov/vuln/detail/CVE-2026-55893
- https://github.com/capstone-engine/capstone/commit/09e76802380b9e94d9720c44458d9d5282219e7e
- https://github.com/capstone-engine/capstone/commit/e17ee44a8307ea33375b4727ac4f987650bf7bed
- https://github.com/capstone-engine/capstone/pull/2968
- https://github.com/capstone-engine/capstone/pull/2969
