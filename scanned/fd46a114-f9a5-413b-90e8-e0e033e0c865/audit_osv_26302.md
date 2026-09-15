# [H] wifi: ath12k: fix dfs-radar and temperature event locking

## Summary
Severity: High
Advisory: CVE-2023-52776
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52776
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: fix dfs-radar and temperature event locking

The ath12k active pdevs are protected by RCU but the DFS-radar and
temperature event handling code calling ath12k_mac_get_ar_by_pdev_id()
was not marked as a read-side critical section.

Mark the code in question as RCU read-side critical sections to avoid
any potential use-after-free issues.

Note that the temperature event handler looks like a place holder
currently but would still trigger an RCU lockdep splat.

Compile tested only.

## References
- https://git.kernel.org/stable/c/69bd216e049349886405b1c87a55dce3d35d1ba7
- https://git.kernel.org/stable/c/774de37c147fea81f2c2e4be5082304f4f71d535
- https://git.kernel.org/stable/c/d7a5f7f76568e48869916d769e28b9f3ca70c78e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52776.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52776
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
