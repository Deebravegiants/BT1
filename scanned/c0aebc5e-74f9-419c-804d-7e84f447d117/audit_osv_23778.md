# [M] spi: spi-fsl-qspi: check return value after calling platform_get_resource_byname()

## Summary
Severity: Medium
Advisory: CVE-2022-49475
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49475
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: spi-fsl-qspi: check return value after calling platform_get_resource_byname()

It will cause null-ptr-deref if platform_get_resource_byname() returns NULL,
we need check the return value.

## References
- https://git.kernel.org/stable/c/10f537219629769498ecb8515e096be213224c24
- https://git.kernel.org/stable/c/33dda87d04598ac5d9a849218a373443f7d3de66
- https://git.kernel.org/stable/c/560dcbe1c7a78f597f2167371ebdbe2bca3d0735
- https://git.kernel.org/stable/c/9d9c84825c3ec359b165c762a424cfdefe87fdd7
- https://git.kernel.org/stable/c/a2b331ac11e1cac56f5b7d367e9f3c5796deaaed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49475.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49475
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
