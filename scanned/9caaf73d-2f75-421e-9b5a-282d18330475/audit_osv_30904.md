# [H] EDAC/igen6: Avoid segmentation fault on module unload

## Summary
Severity: High
Advisory: CVE-2024-56708
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56708
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

EDAC/igen6: Avoid segmentation fault on module unload

The segmentation fault happens because:

During modprobe:
1. In igen6_probe(), igen6_pvt will be allocated with kzalloc()
2. In igen6_register_mci(), mci->pvt_info will point to
   &igen6_pvt->imc[mc]

During rmmod:
1. In mci_release() in edac_mc.c, it will kfree(mci->pvt_info)
2. In igen6_remove(), it will kfree(igen6_pvt);

Fix this issue by setting mci->pvt_info to NULL to avoid the double
kfree.

## References
- https://git.kernel.org/stable/c/029ac07bb92d2f7502d47a4916f197a8445d83bf
- https://git.kernel.org/stable/c/2a80e710bbc088a2511c159ee4d910456c5f0832
- https://git.kernel.org/stable/c/830cabb61113d92a425dd3038ccedbdfb3c8d079
- https://git.kernel.org/stable/c/db60326f2c47b079e36785ace621eb3002db2088
- https://git.kernel.org/stable/c/e5c7052664b61f9e2f896702d20552707d0ef60a
- https://git.kernel.org/stable/c/fefaae90398d38a1100ccd73b46ab55ff4610fba
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56708.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56708
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
