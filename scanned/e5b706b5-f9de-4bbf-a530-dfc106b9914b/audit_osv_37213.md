# [H] CVE-2026-29645

## Summary
Severity: High
Advisory: CVE-2026-29645
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-29645
Type: osv

## Details
NEMU (OpenXiangShan/NEMU) before v2025.12.r2 contains an improper instruction-validation flaw in its RISC-V Vector (RVV) decoder. The decoder does not correctly validate the funct3 field when decoding vsetvli/vsetivli/vsetvl, allowing certain invalid OP-V instruction encodings to be misinterpreted and executed as vset* configuration instructions rather than raising an illegal-instruction exception. This can be exploited by providing crafted RISC-V binaries to cause incorrect trap behavior, architectural state corruption/divergence, and potential denial of service in systems that rely on NEMU for correct execution or sandboxing.

## References
- https://docs.riscv.org/reference/isa/unpriv/v-st-ext.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29645.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29645
- https://github.com/OpenXiangShan/NEMU/issues/952
- https://github.com/OpenXiangShan/NEMU/commit/481de637d5fc5838356caee80a79e56a33754039
- https://github.com/OpenXiangShan/NEMU/pull/958
