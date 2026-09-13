# [M] EDAC/highbank: Fix memory leak in highbank_mc_probe()

## Summary
Severity: Medium
Advisory: CVE-2022-49757
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49757
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <4.14.305, >=4.15.0 <4.19.272, >=4.20.0 <5.4.231, >=5.5.0 <5.10.166, >=5.11.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

EDAC/highbank: Fix memory leak in highbank_mc_probe()

When devres_open_group() fails, it returns -ENOMEM without freeing memory
allocated by edac_mc_alloc().

Call edac_mc_free() on the error handling path to avoid a memory leak.

  [ bp: Massage commit message. ]

## References
- https://git.kernel.org/stable/c/0db40e23b56d217eebd385bebb64057ef764b2c7
- https://git.kernel.org/stable/c/329fbd260352a7b9a83781d8b8bd96f95844a51f
- https://git.kernel.org/stable/c/8d23f5d25264beb223ee79cdb530b88c237719fc
- https://git.kernel.org/stable/c/b7863ef8a8f0fee96b4eb41211f4918c0e047253
- https://git.kernel.org/stable/c/caffa7fed1397d1395052272c93900176de86557
- https://git.kernel.org/stable/c/e7a293658c20a7945014570e1921bf7d25d68a36
- https://git.kernel.org/stable/c/f1b3e23ed8df87d779ee86ac37f379e79a24169a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49757.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49757
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
