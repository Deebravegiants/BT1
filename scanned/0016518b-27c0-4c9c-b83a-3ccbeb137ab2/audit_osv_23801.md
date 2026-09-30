# [H] wl1251: dynamically allocate memory used for DMA

## Summary
Severity: High
Advisory: CVE-2022-49500
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49500
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wl1251: dynamically allocate memory used for DMA

With introduction of vmap'ed stacks, stack parameters can no
longer be used for DMA and now leads to kernel panic.

It happens at several places for the wl1251 (e.g. when
accessed through SDIO) making it unuseable on e.g. the
OpenPandora.

We solve this by allocating temporary buffers or use wl1251_read32().

Tested on v5.18-rc5 with OpenPandora.

## References
- https://git.kernel.org/stable/c/454744754cbf2c21b3fc7344e46e10bee2768094
- https://git.kernel.org/stable/c/da03bbfbf5acd1ab0b074617e865ad1e8a5779ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49500.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49500
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
