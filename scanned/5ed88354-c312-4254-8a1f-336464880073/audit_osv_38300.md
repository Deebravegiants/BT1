# [H] CVE-2026-37540

## Summary
Severity: High
Advisory: CVE-2026-37540
CVSS: 8.4 (CVSS:3.1/AC:L/AV:L/A:H/C:H/I:H/PR:N/S:U/UI:N)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-37540
Type: osv

## Details
OpenAMP v2025.10.0 ELF loader contains an integer overflow vulnerability in firmware image parsing. In elf_loader.c, it performs multiplication of two attacker-controlled 16-bit values from the ELF header without overflow checking. On 32-bit embedded systems (STM32MP1, Zynq, i.MX), large values can cause the product to wrap around to a small value.

## References
- https://gist.github.com/sgInnora/f4ac66faeefe07a653ceeb3f58cdc381
- https://github.com/OpenAMP/open-amp/blob/main/lib/remoteproc/elf_loader.c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37540.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-37540
- https://github.com/OpenAMP/open-amp
