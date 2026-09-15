# [M] wifi: ath11k: fix htt pktlog locking

## Summary
Severity: Medium
Advisory: CVE-2023-52800
Ecosystem: Linux
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52800
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.202, >=5.11.0 <5.15.140, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath11k: fix htt pktlog locking

The ath11k active pdevs are protected by RCU but the htt pktlog handling
code calling ath11k_mac_get_ar_by_pdev_id() was not marked as a
read-side critical section.

Mark the code in question as an RCU read-side critical section to avoid
any potential use-after-free issues.

Compile tested only.

## References
- https://git.kernel.org/stable/c/03ed26935bebf6b6fd8a656490bf3dcc71b72679
- https://git.kernel.org/stable/c/3a51e6b4da71fdfa43ec006d6abc020f3e22d14e
- https://git.kernel.org/stable/c/3f77c7d605b29df277d77e9ee75d96e7ad145d2d
- https://git.kernel.org/stable/c/423762f021825b5e57c3d6f01ff96a9ff19cdcd8
- https://git.kernel.org/stable/c/69cede2a5a5f60e3f5602b901b52cb64edd2ea6c
- https://git.kernel.org/stable/c/e3199b3fac65c9f103055390b6fd07c5cffa5961
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52800.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52800
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
