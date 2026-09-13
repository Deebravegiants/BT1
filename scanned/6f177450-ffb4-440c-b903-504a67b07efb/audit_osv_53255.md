# [H] CVE-2022-34918

## Summary
Severity: High
Advisory: CVE-2022-34918
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-04
Source: https://osv.dev/vulnerability/CVE-2022-34918
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.18.9. A type confusion bug in nft_set_elem_init (leading to a buffer overflow) could be used by a local attacker to escalate privileges, a different vulnerability than CVE-2022-32250. (The attacker can obtain root access, but must start with an unprivileged user namespace to obtain CAP_NET_ADMIN access.) This can be fixed in nft_setelem_parse_data in net/netfilter/nf_tables_api.c.

## References
- https://lore.kernel.org/netfilter-devel/cd9428b6-7ffb-dd22-d949-d86f4869f452%40randorisec.fr/T/#u
- https://www.debian.org/security/2022/dsa-5191
- http://packetstormsecurity.com/files/168191/Kernel-Live-Patch-Security-Notice-LSN-0089-1.html
- http://www.openwall.com/lists/oss-security/2022/08/06/5
- https://security.netapp.com/advisory/ntap-20220826-0004/
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/?id=7e6bc1f6cabcd30aba0b11219d8e01b952eacbb6
- https://www.openwall.com/lists/oss-security/2022/07/02/3
- https://www.randorisec.fr/crack-linux-firewall/
- http://packetstormsecurity.com/files/168543/Netfilter-nft_set_elem_init-Heap-Overflow-Privilege-Escalation.html
- http://www.openwall.com/lists/oss-security/2022/07/05/1
