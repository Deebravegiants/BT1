# [M] soc: bcm: brcmstb: pm: pm-arm: Fix refcount leak in brcmstb_pm_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49678
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49678
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.250, >=4.20.0 <5.4.202, >=5.5.0 <5.10.127, >=5.11.0 <5.15.51, >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

soc: bcm: brcmstb: pm: pm-arm: Fix refcount leak in brcmstb_pm_probe

of_find_matching_node() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
Add missing of_node_put() to avoid refcount leak.

In brcmstb_init_sram, it pass dn to of_address_to_resource(),
of_address_to_resource() will call of_find_device_by_node() to take
reference, so we should release the reference returned by
of_find_matching_node().

## References
- https://git.kernel.org/stable/c/10ba9d499a9fd82ed40897e734ba19870a879407
- https://git.kernel.org/stable/c/30bbfeb480ae8b5ee43199d72417b232590440c2
- https://git.kernel.org/stable/c/37d838de369b07b596c19ff3662bf0293fdb09ee
- https://git.kernel.org/stable/c/4f5877bdf7b593e988f1924f4c3df6523f80b39c
- https://git.kernel.org/stable/c/734a4d15142bb4c8ecad2d8ec70d7564e78ae34d
- https://git.kernel.org/stable/c/dcafd5463d8f20c4f90ddc138a5738adb99f74c8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49678.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49678
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
