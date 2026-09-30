# [M] mtd: rawnand: cadence: fix possible null-ptr-deref in cadence_nand_dt_probe()

## Summary
Severity: Medium
Advisory: CVE-2022-49494
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49494
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtd: rawnand: cadence: fix possible null-ptr-deref in cadence_nand_dt_probe()

It will cause null-ptr-deref when using 'res', if platform_get_resource()
returns NULL, so move using 'res' after devm_ioremap_resource() that
will check it to avoid null-ptr-deref.
And use devm_platform_get_and_ioremap_resource() to simplify code.

## References
- https://git.kernel.org/stable/c/069af5e27c1b0f7677ef76d8d3102e503ca4f80b
- https://git.kernel.org/stable/c/0cfee868b89ffa945f3d535ee5c985cb40c5a0f8
- https://git.kernel.org/stable/c/13b60d3dc84b47307669edb66b633b18466014b4
- https://git.kernel.org/stable/c/81f1ddffdc22ca5789e33b9d4712914e302090c1
- https://git.kernel.org/stable/c/a28ed09dafee20da51eb26452950839633afd824
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49494.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49494
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
