# [M] Capstone has a NULL Pointer Dereference with 3DNow! opcodes

## Summary
Severity: Medium
Advisory: CVE-2026-47143
Aliases: GHSA-289w-cm54-fgrm, PYSEC-2026-3544
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-47143
Type: osv

## Details
Capstone is a disassembly framework. Versions prior to 6.0.0-Alpha8 and 5.0.8 have a NULL pointer dereference in `modRMRequired()` and `decode()` when disassembling 3DNow! opcodes (`0F 0F`) in builds compiled with `-DCAPSTONE_X86_REDUCE`, allowing a remote attacker to crash any application using the reduced X86 Capstone library by supplying a crafted input containing the 4-byte sequence `0F 0F <modrm> <imm8>`. Versions 6.0.0-Alpha8 and 5.0.8 patch the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47143.json
- https://github.com/capstone-engine/capstone/security/advisories/GHSA-289w-cm54-fgrm
- https://nvd.nist.gov/vuln/detail/CVE-2026-47143
- https://github.com/capstone-engine/capstone/commit/a0201371719b5aaa91d318ab2898843718f92d1f
- https://github.com/capstone-engine/capstone/commit/fab595205fee206f5c21be6ed8ad2eaf9225f1c7
- https://github.com/capstone-engine/capstone/pull/2924
