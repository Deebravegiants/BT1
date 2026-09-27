# [H] nvme-multipath: fix lockdep WARN due to partition scan work

## Summary
Severity: High
Advisory: CVE-2025-68218
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68218
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.159, >=6.2.0 <6.6.118, >=6.7.0 <6.12.60, >=6.12.0 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-multipath: fix lockdep WARN due to partition scan work

Blktests test cases nvme/014, 057 and 058 fail occasionally due to a
lockdep WARN. As reported in the Closes tag URL, the WARN indicates that
a deadlock can happen due to the dependency among disk->open_mutex,
kblockd workqueue completion and partition_scan_work completion.

To avoid the lockdep WARN and the potential deadlock, cut the dependency
by running the partition_scan_work not by kblockd workqueue but by
nvme_wq.

## References
- https://git.kernel.org/stable/c/6d87cd5335784351280f82c47cc8a657271929c3
- https://git.kernel.org/stable/c/89456dab7ba5ab63d60945440926673a3205e829
- https://git.kernel.org/stable/c/b03eb63288a8ffe3adfb34e68309c8e2edb06d0b
- https://git.kernel.org/stable/c/e2a897ad5f538d314955c747a0a2edb184fcdecd
- https://git.kernel.org/stable/c/ef4ab2a8abe554379e10303ae86f7c501336ba0d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68218.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68218
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
