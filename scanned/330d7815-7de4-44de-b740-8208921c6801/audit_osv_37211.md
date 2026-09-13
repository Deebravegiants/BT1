# [H] CVE-2026-29642

## Summary
Severity: High
Advisory: CVE-2026-29642
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-29642
Type: osv

## Details
A local attacker who can execute privileged CSR operations (or can induce firmware to do so) performs carefully crafted reads/writes to menvcfg (e.g., csrrs in M-mode). On affected XiangShan versions (commit aecf601e803bfd2371667a3fb60bfcd83c333027, 2024-11-19), these menvcfg accesses can unexpectedly set WPRI (reserved) bits in the status view (xstatus) to 1. RISC-V defines WPRI fields as "writes preserve values, reads ignore values," i.e., they must not be modified by software manipulating other fields, and menvcfg itself contains multiple WPRI fields.

## References
- https://docs.riscv.org/reference/isa/priv/machine.html
- https://docs.riscv.org/reference/isa/priv/priv-csrs.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29642.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29642
- https://github.com/OpenXiangShan/XiangShan/issues/3934
- https://github.com/OpenXiangShan/XiangShan/commit/5e3dd63
