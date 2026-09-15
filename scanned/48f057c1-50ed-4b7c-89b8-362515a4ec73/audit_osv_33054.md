# [H] proc: use the same treatment to check proc_lseek as ones for proc_read_iter et.al

## Summary
Severity: High
Advisory: CVE-2025-38653
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38653
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.148, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

proc: use the same treatment to check proc_lseek as ones for proc_read_iter et.al

Check pde->proc_ops->proc_lseek directly may cause UAF in rmmod scenario. 
It's a gap in proc_reg_open() after commit 654b33ada4ab("proc: fix UAF in
proc_get_inode()").  Followed by AI Viro's suggestion, fix it in same
manner.

## References
- https://git.kernel.org/stable/c/1fccbfbae1dd36198dc47feac696563244ad81d3
- https://git.kernel.org/stable/c/33c778ea0bd0fa62ff590497e72562ff90f82b13
- https://git.kernel.org/stable/c/c35b0feb80b48720dfbbf4e33759c7be3faaebb6
- https://git.kernel.org/stable/c/d136502e04d8853a9aecb335d07bbefd7a1519a8
- https://git.kernel.org/stable/c/fc1072d934f687e1221d685cf1a49a5068318f34
- https://git.kernel.org/stable/c/ff7ec8dc1b646296f8d94c39339e8d3833d16c05
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38653.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38653
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
