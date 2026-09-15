# [H] objtool, spi: amd: Fix out-of-bounds stack access in amd_set_spi_freq()

## Summary
Severity: High
Advisory: CVE-2025-40014
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-40014
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

objtool, spi: amd: Fix out-of-bounds stack access in amd_set_spi_freq()

If speed_hz < AMD_SPI_MIN_HZ, amd_set_spi_freq() iterates over the
entire amd_spi_freq array without breaking out early, causing 'i' to go
beyond the array bounds.

Fix that by stopping the loop when it gets to the last entry, so the low
speed_hz value gets clamped up to AMD_SPI_MIN_HZ.

Fixes the following warning with an UBSAN kernel:

  drivers/spi/spi-amd.o: error: objtool: amd_set_spi_freq() falls through to next function amd_spi_set_opcode()

## References
- https://git.kernel.org/stable/c/76e51db43fe4aaaebcc5ddda67b0807f7c9bdecc
- https://git.kernel.org/stable/c/7f2c746e09a3746bf937bc708129dc8af61d8f19
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40014.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40014
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
