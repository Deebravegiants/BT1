# [H] dmaengine: ti: k3-udma-glue: Fix of_k3_udma_glue_parse_chn_by_id()

## Summary
Severity: High
Advisory: CVE-2024-40991
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40991
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.9.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: ti: k3-udma-glue: Fix of_k3_udma_glue_parse_chn_by_id()

The of_k3_udma_glue_parse_chn_by_id() helper function erroneously
invokes "of_node_put()" on the "udmax_np" device-node passed to it,
without having incremented its reference count at any point. Fix it.

## References
- https://git.kernel.org/stable/c/a5ab5f413d1e4c7ed5f64271b025f0726374509e
- https://git.kernel.org/stable/c/ba27e9d2207784da748b19170a2e56bd7770bd81
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40991.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40991
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
