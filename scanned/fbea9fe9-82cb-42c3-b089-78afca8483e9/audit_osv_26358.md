# [M] mm/swapfile: add cond_resched() in get_swap_pages()

## Summary
Severity: Medium
Advisory: CVE-2023-52932
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52932
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <4.14.306, >=4.15.0 <4.19.273, >=4.20.0 <5.4.232, >=5.5.0 <5.10.168, >=5.11.0 <5.15.93, >=5.16.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/swapfile: add cond_resched() in get_swap_pages()

The softlockup still occurs in get_swap_pages() under memory pressure.  64
CPU cores, 64GB memory, and 28 zram devices, the disksize of each zram
device is 50MB with same priority as si.  Use the stress-ng tool to
increase memory pressure, causing the system to oom frequently.

The plist_for_each_entry_safe() loops in get_swap_pages() could reach tens
of thousands of times to find available space (extreme case:
cond_resched() is not called in scan_swap_map_slots()).  Let's add
cond_resched() into get_swap_pages() when failed to find available space
to avoid softlockup.

## References
- https://git.kernel.org/stable/c/29f0349c5c76b627fe06b87d4b13fa03a6ce8e64
- https://git.kernel.org/stable/c/30187be29052bba9203b0ae2bdd815e0bc2faaab
- https://git.kernel.org/stable/c/387217b97e99699c34e6d95ce2b91b327fcd853e
- https://git.kernel.org/stable/c/49178d4d61e78aed8c837dfeea8a450700f196e2
- https://git.kernel.org/stable/c/5dbe1ebd56470d03b78fc31491a9e4d433106ef2
- https://git.kernel.org/stable/c/7717fc1a12f88701573f9ed897cc4f6699c661e3
- https://git.kernel.org/stable/c/d49c85a1913385eed46dd16a25ad0928253767f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52932.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52932
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
