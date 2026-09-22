# [H] CVE-2021-23134

## Summary
Severity: High
Advisory: CVE-2021-23134
Aliases: A-188883590, PUB-A-188883590
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-12
Source: https://osv.dev/vulnerability/CVE-2021-23134
Type: osv

## Details
Use After Free vulnerability in nfc sockets in the Linux Kernel before 5.12.4 allows local attackers to elevate their privileges. In typical configurations, the issue can only be triggered by a privileged local user with the CAP_NET_RAW capability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LZYORWNQIHNWRFYRDXBWYWBYM46PDZEN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QALNQT4LJFVSSA3MWCIECVY4AFPP4X77/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://security.netapp.com/advisory/ntap-20210625-0007/
- https://www.openwall.com/lists/oss-security/2021/05/11/4
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/?id=c61760e6940d
