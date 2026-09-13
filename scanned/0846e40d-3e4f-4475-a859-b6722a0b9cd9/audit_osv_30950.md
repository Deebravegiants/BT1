# [M] powerpc/prom_init: Fixup missing powermac #size-cells

## Summary
Severity: Medium
Advisory: CVE-2024-56781
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-56781
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/prom_init: Fixup missing powermac #size-cells

On some powermacs `escc` nodes are missing `#size-cells` properties,
which is deprecated and now triggers a warning at boot since commit
045b14ca5c36 ("of: WARN on deprecated #address-cells/#size-cells
handling").

For example:

  Missing '#size-cells' in /pci@f2000000/mac-io@c/escc@13000
  WARNING: CPU: 0 PID: 0 at drivers/of/base.c:133 of_bus_n_size_cells+0x98/0x108
  Hardware name: PowerMac3,1 7400 0xc0209 PowerMac
  ...
  Call Trace:
    of_bus_n_size_cells+0x98/0x108 (unreliable)
    of_bus_default_count_cells+0x40/0x60
    __of_get_address+0xc8/0x21c
    __of_address_to_resource+0x5c/0x228
    pmz_init_port+0x5c/0x2ec
    pmz_probe.isra.0+0x144/0x1e4
    pmz_console_init+0x10/0x48
    console_init+0xcc/0x138
    start_kernel+0x5c4/0x694

As powermacs boot via prom_init it's possible to add the missing
properties to the device tree during boot, avoiding the warning. Note
that `escc-legacy` nodes are also missing `#size-cells` properties, but
they are skipped by the macio driver, so leave them alone.

Depends-on: 045b14ca5c36 ("of: WARN on deprecated #address-cells/#size-cells handling")

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
- https://git.kernel.org/stable/c/0b94d838018fb0a824e0cd3149034928c99fb1b7
- https://git.kernel.org/stable/c/296a109fa77110ba5267fe0e90a26005eecc2726
- https://git.kernel.org/stable/c/691284c2cd33ffaa0b35ce53b3286b90621e9dc9
- https://git.kernel.org/stable/c/6d5f0453a2228607333bff0c85238a3cb495d194
- https://git.kernel.org/stable/c/a79a7e3c03ae2a07f68b5f24d5ed549f9799ec89
- https://git.kernel.org/stable/c/cf89c9434af122f28a3552e6f9cc5158c33ce50a
- https://git.kernel.org/stable/c/ee68554d2c03e32077f7b984e5289fdb005036d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56781.json
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-56781
