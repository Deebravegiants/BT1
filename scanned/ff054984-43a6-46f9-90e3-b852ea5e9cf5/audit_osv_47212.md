# [C] CVE-2016-10764

## Summary
Severity: Critical
Advisory: CVE-2016-10764
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-27
Source: https://osv.dev/vulnerability/CVE-2016-10764
Type: osv

## Details
In the Linux kernel before 4.9.6, there is an off by one in the drivers/mtd/spi-nor/cadence-quadspi.c cqspi_setup_flash() function. There are CQSPI_MAX_CHIPSELECT elements in the ->f_pdata array so the ">" should be ">=" instead.

## References
- https://support.f5.com/csp/article/K24444495?utm_source=f5support&amp%3Butm_medium=RSS
- https://mirrors.edge.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.6
- https://support.f5.com/csp/article/K24444495
- https://github.com/torvalds/linux/commit/193e87143c290ec16838f5368adc0e0bc94eb931
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=193e87143c290ec16838f5368adc0e0bc94eb931
