# [M] mtd: rawnand: intel: fix possible null-ptr-deref in ebu_nand_probe()

## Summary
Severity: Medium
Advisory: CVE-2022-49487
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49487
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtd: rawnand: intel: fix possible null-ptr-deref in ebu_nand_probe()

It will cause null-ptr-deref when using 'res', if platform_get_resource()
returns NULL, so move using 'res' after devm_ioremap_resource() that
will check it to avoid null-ptr-deref.

## References
- https://git.kernel.org/stable/c/daa5166450b447415aeeaac0199e445bae7bd0f2
- https://git.kernel.org/stable/c/ddf66aefd685fd46500b9917333e1b1e118276dc
- https://git.kernel.org/stable/c/e5b1e419cdb6dd8709eb05ed34039a3ded8e6003
- https://git.kernel.org/stable/c/f8e262eb7575a4a2412f30f7a1b293875aceba80
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49487.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49487
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
