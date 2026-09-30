# [H] wifi: ath12k: fix htt mlo-offset event locking

## Summary
Severity: High
Advisory: CVE-2023-52769
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52769
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: fix htt mlo-offset event locking

The ath12k active pdevs are protected by RCU but the htt mlo-offset
event handling code calling ath12k_mac_get_ar_by_pdev_id() was not
marked as a read-side critical section.

Mark the code in question as an RCU read-side critical section to avoid
any potential use-after-free issues.

Compile tested only.

## References
- https://git.kernel.org/stable/c/6afc57ea315e0f660b1f870a681737bb7b71faef
- https://git.kernel.org/stable/c/afd3425bd69610f318403084fe491e24a1357fb9
- https://git.kernel.org/stable/c/d908ca431e20b0e4bfc5d911d1744910ed779bdb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52769.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52769
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
