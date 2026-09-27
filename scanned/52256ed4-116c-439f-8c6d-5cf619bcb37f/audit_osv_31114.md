# [M] wifi: mt76: mt7925: fix NULL deref check in mt7925_change_vif_links

## Summary
Severity: Medium
Advisory: CVE-2024-57989
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57989
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: mt7925: fix NULL deref check in mt7925_change_vif_links

In mt7925_change_vif_links() devm_kzalloc() may return NULL but this
returned value is not checked.

## References
- https://git.kernel.org/stable/c/2f709fe755c16b811ba7339ae4c3ee2c72323d3d
- https://git.kernel.org/stable/c/5872530c2862700070223a2c2ea85642bf2f8875
- https://git.kernel.org/stable/c/5cd0bd815c8a48862a296df9b30e0ea0da14acd3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57989.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57989
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
