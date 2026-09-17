# [H] CVE-2023-1078

## Summary
Severity: High
Advisory: CVE-2023-1078
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-1078
Type: osv

## Details
A flaw was found in the Linux Kernel in RDS (Reliable Datagram Sockets) protocol. The rds_rm_zerocopy_callback() uses list_entry() on the head of a list causing a type confusion. Local user can trigger this with rds_message_put(). Type confusion leads to `struct rds_msg_zcopy_info *info` actually points to something else that is potentially controlled by local user. It is known how to trigger this, which causes an out of bounds access, and a lock corruption.

## References
- http://www.openwall.com/lists/oss-security/2023/11/05/1
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://security.netapp.com/advisory/ntap-20230505-0004/
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git/commit/?id=f753a68980cf4b59a80fe677619da2b1804f526d
