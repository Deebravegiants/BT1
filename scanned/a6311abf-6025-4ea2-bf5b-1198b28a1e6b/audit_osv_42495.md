# [H] net/mlx5: Fix MCIA register buffer overflow on 32 dword reads

## Summary
Severity: High
Advisory: CVE-2026-68293
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68293
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: Fix MCIA register buffer overflow on 32 dword reads

The MCIA register can return up to 32 dwords (128 bytes) when the device
advertises the mcia_32dwords capability, but struct
mlx5_ifc_mcia_reg_bits only defines dword_0..11, leaving room for just
12 dwords (48 bytes) of data.

mlx5_query_mcia() clamps the read size to mlx5_mcia_max_bytes() and then
memcpy()s that many bytes out of the register, potentially reading past
the end of the 'out' buffer. On kernels built with FORTIFY_SOURCE this
is caught as a buffer overflow while reading the module EEPROM via
ethtool:

  detected buffer overflow in memcpy
  kernel BUG at lib/string_helpers.c:1048!
  RIP: 0010:fortify_panic+0x13/0x20
  Call Trace:
   mlx5_query_mcia.isra.0+0x200/0x210 [mlx5_core]
   mlx5_query_module_eeprom_by_page+0x4a/0xa0 [mlx5_core]
   mlx5e_get_module_eeprom_by_page+0xbb/0x120 [mlx5_core]
   eeprom_prepare_data+0xf3/0x170
   ethnl_default_doit+0xf1/0x3b0

Extend the mcia_reg layout to 32 dwords.

## References
- https://git.kernel.org/stable/c/11c057d23465c7a5817a7284c896d19d54c0b616
- https://git.kernel.org/stable/c/5be4eebd5a3a198dab0adcd550e1cadca79bdfed
- https://git.kernel.org/stable/c/87b39a8c875ca744b7de69af0a8ef8874cffccf1
- https://git.kernel.org/stable/c/88b2a16ddac3357e3f1d528e758b51e2c945d546
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68293.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68293
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
