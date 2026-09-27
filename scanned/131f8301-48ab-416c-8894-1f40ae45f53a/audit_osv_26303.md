# [H] wifi: ath11k: fix gtk offload status event locking

## Summary
Severity: High
Advisory: CVE-2023-52777
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52777
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath11k: fix gtk offload status event locking

The ath11k active pdevs are protected by RCU but the gtk offload status
event handling code calling ath11k_mac_get_arvif_by_vdev_id() was not
marked as a read-side critical section.

Mark the code in question as an RCU read-side critical section to avoid
any potential use-after-free issues.

Compile tested only.

## References
- https://git.kernel.org/stable/c/0cf7577b6b3153b4b49deea9719fe43f96469c6d
- https://git.kernel.org/stable/c/1dea3c0720a146bd7193969f2847ccfed5be2221
- https://git.kernel.org/stable/c/cf9c7d783a2bf9305df4ef5b93d9063a52e18fca
- https://git.kernel.org/stable/c/e83246ecd3b193f8d91fce778e8a5ba747fc7d8a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52777.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52777
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
