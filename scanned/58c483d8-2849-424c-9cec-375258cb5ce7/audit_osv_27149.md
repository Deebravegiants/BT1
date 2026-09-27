# [C] arch: riscv: userspace: potential security risk when CONFIG_RISCV_GP=y

## Summary
Severity: Critical
Advisory: CVE-2024-11263
Aliases: GHSA-jjf3-7x72-pqm9
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-11263
Type: osv

## Details
When the Global Pointer (GP) relative addressing is enabled (CONFIG_RISCV_GP=y), the gp reg points at 0x800 bytes past the start of the .sdata section which is then used by the linker to relax accesses to global symbols.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11263.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-jjf3-7x72-pqm9
- https://nvd.nist.gov/vuln/detail/CVE-2024-11263
- https://github.com/zephyrproject-rtos/zephyr
