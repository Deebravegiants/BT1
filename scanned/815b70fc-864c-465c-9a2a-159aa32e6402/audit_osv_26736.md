# [H] net: sched: cls_u32: Undo tcf_bind_filter if u32_replace_hw_knode

## Summary
Severity: High
Advisory: CVE-2023-53733
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-24
Source: https://osv.dev/vulnerability/CVE-2023-53733
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <6.1.42, >=6.2.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sched: cls_u32: Undo tcf_bind_filter if u32_replace_hw_knode

When u32_replace_hw_knode fails, we need to undo the tcf_bind_filter
operation done at u32_set_parms.

## References
- https://git.kernel.org/stable/c/025159ed118ba5145b241d574edadb0e00d3c20f
- https://git.kernel.org/stable/c/9cb36faedeafb9720ac236aeae2ea57091d90a09
- https://git.kernel.org/stable/c/a9345793469b65ee5ba7b033239916c2a67d3dd4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53733.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53733
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
