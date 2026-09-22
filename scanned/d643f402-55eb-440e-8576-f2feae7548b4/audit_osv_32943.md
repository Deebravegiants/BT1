# [H] NFSv4/pNFS: Fix a race to wake on NFS_LAYOUT_DRAIN

## Summary
Severity: High
Advisory: CVE-2025-38393
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38393
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.240, >=5.11.0 <5.15.187, >=5.16.0 <6.1.144, >=5.19.0 <6.6.97, >=6.2.0 <6.12.37, >=6.7.0 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSv4/pNFS: Fix a race to wake on NFS_LAYOUT_DRAIN

We found a few different systems hung up in writeback waiting on the same
page lock, and one task waiting on the NFS_LAYOUT_DRAIN bit in
pnfs_update_layout(), however the pnfs_layout_hdr's plh_outstanding count
was zero.

It seems most likely that this is another race between the waiter and waker
similar to commit ed0172af5d6f ("SUNRPC: Fix a race to wake a sync task").
Fix it up by applying the advised barrier.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/08287df60bac5b008b6bcdb03053988335d3d282
- https://git.kernel.org/stable/c/1f4da20080718f258e189a2c5f515385fa393da6
- https://git.kernel.org/stable/c/864a54c1243ed3ca60baa4bc492dede1361f4c83
- https://git.kernel.org/stable/c/8846fd02c98da8b79e6343a20e6071be6f372180
- https://git.kernel.org/stable/c/8ca65fa71024a1767a59ffbc6a6e2278af84735e
- https://git.kernel.org/stable/c/c01776287414ca43412d1319d2877cbad65444ac
- https://git.kernel.org/stable/c/e4b13885e7ef1e64e45268feef1e5f0707c47e72
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38393.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38393
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
