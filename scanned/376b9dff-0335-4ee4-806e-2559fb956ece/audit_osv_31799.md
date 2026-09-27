# [H] NFSD: fix hang in nfsd4_shutdown_callback

## Summary
Severity: High
Advisory: CVE-2025-21795
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21795
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=5.19.0 <6.6.79, >=6.2.0 <6.12.16, >=6.7.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: fix hang in nfsd4_shutdown_callback

If nfs4_client is in courtesy state then there is no point to send
the callback. This causes nfsd4_shutdown_callback to hang since
cl_cb_inflight is not 0. This hang lasts about 15 minutes until TCP
notifies NFSD that the connection was dropped.

This patch modifies nfsd4_run_cb_work to skip the RPC call if
nfs4_client is in courtesy state.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/036ac2778f7b28885814c6fbc07e156ad1624d03
- https://git.kernel.org/stable/c/23ad7797c74cd8f7f90617f1e59a8703e2b43908
- https://git.kernel.org/stable/c/38d345f612503b850c2973e5a879f88e441b34d7
- https://git.kernel.org/stable/c/abed68027ea3ab893ac85cc46a00e2e64a324239
- https://git.kernel.org/stable/c/cedfbb92cf97a6bff3d25633001d9c44442ee854
- https://git.kernel.org/stable/c/e88d2451cd42e025465d6b51fd716a47b0b3800d
- https://git.kernel.org/stable/c/efa8a261c575f816c7e79a87aeb3ef8a0bd6b221
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21795.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21795
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
