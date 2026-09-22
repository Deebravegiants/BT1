# [M] CVE-2023-42752

## Summary
Severity: Medium
Advisory: CVE-2023-42752
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-13
Source: https://osv.dev/vulnerability/CVE-2023-42752
Type: osv

## Details
An integer overflow flaw was found in the Linux kernel. This issue leads to the kernel allocating `skb_shared_info` in the userspace, which is exploitable in systems without SMAP protection since `skb_shared_info` contains references to function pointers.

## References
- http://packetstormsecurity.com/files/175963/Kernel-Live-Patch-Security-Notice-LSN-0099-1.html
- https://access.redhat.com/security/cve/CVE-2023-42752
- https://bugzilla.redhat.com/show_bug.cgi?id=2239828
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/?id=915d975b2ffa
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/?id=c3b704d4a4a2
