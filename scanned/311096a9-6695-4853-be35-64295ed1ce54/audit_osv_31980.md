# [H] spi: cadence: Fix out-of-bounds array access in cdns_mrvl_xspi_setup_clock()

## Summary
Severity: High
Advisory: CVE-2025-22067
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22067
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: cadence: Fix out-of-bounds array access in cdns_mrvl_xspi_setup_clock()

If requested_clk > 128, cdns_mrvl_xspi_setup_clock() iterates over the
entire cdns_mrvl_xspi_clk_div_list array without breaking out early,
causing 'i' to go beyond the array bounds.

Fix that by stopping the loop when it gets to the last entry, clamping
the clock to the minimum 6.25 MHz.

Fixes the following warning with an UBSAN kernel:

  vmlinux.o: warning: objtool: cdns_mrvl_xspi_setup_clock: unexpected end of section .text.cdns_mrvl_xspi_setup_clock

## References
- https://git.kernel.org/stable/c/645f1813fe0dc96381c36b834131e643b798fd73
- https://git.kernel.org/stable/c/7ba0847fa1c22e7801cebfe5f7b75aee4fae317e
- https://git.kernel.org/stable/c/c1fb84e274cb6a2bce6ba5e65116c06e0b3ab275
- https://git.kernel.org/stable/c/e50781bf7accc75883cb8a6a9921fb4e2fa8cca4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22067.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22067
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
