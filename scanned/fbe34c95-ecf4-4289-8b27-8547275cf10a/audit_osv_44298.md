# [H] pmdomain: mediatek: fix remaining %pOF after of_node_put()

## Summary
Severity: High
Advisory: CVE-2026-80750
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80750
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

pmdomain: mediatek: fix remaining %pOF after of_node_put()

scpsys_get_bus_protection_legacy() looks up several legacy bus
protection regmaps from device-tree nodes.

Two error paths put the device node before checking whether the regmap
lookup failed, but still pass that node to dev_err_probe() with %pOF on
failure. If of_node_put() drops the last reference, the later %pOF
formatting can dereference a freed device node.

Keep the node reference until after the error message has been emitted in
the infracfg and SMI lookup paths. Also drop the SMI node before
returning when the SMI phandle is missing.

## References
- https://git.kernel.org/stable/c/10bf2d7261d7f724ed43a09eea4c90c19c0230a0
- https://git.kernel.org/stable/c/3e013bc8b941bd52c8e3a99798d0ae8792cb71ca
- https://git.kernel.org/stable/c/970b9c83a07c405fdd32bcce7cc4c9e670e58875
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80750.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80750
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
