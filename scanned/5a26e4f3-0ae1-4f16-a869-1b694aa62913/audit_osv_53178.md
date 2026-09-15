# [H] CVE-2022-32250

## Summary
Severity: High
Advisory: CVE-2022-32250
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/CVE-2022-32250
Type: osv

## Details
net/netfilter/nf_tables_api.c in the Linux kernel through 5.18.1 allows a local user (able to create user/net namespaces) to escalate privileges to root because an incorrect NFT_STATEFUL_EXPR check leads to a use-after-free.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MO6Y3TC4WUUNKRP7OQA26OVTZTPCS6F2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UIZTJOJCVVEJVOQSCHE6IJQKMPISHQ5L/
- http://www.openwall.com/lists/oss-security/2022/06/20/1
- http://www.openwall.com/lists/oss-security/2022/07/03/6
- https://security.netapp.com/advisory/ntap-20220715-0005/
- https://www.debian.org/security/2022/dsa-5161
- http://www.openwall.com/lists/oss-security/2022/07/03/5
- http://www.openwall.com/lists/oss-security/2022/09/02/9
- https://lists.debian.org/debian-lts-announce/2022/07/msg00000.html
- https://www.debian.org/security/2022/dsa-5173
- https://bugzilla.redhat.com/show_bug.cgi?id=2092427
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/net/netfilter?id=520778042ccca019f3ffa136dd0ca565c486cedd
- http://www.openwall.com/lists/oss-security/2022/06/03/1
- https://www.openwall.com/lists/oss-security/2022/05/31/1
- http://www.openwall.com/lists/oss-security/2022/06/04/1
- http://www.openwall.com/lists/oss-security/2022/08/25/1
- https://github.com/theori-io/CVE-2022-32250-exploit
- https://blog.theori.io/research/CVE-2022-32250-linux-kernel-lpe-2022/
