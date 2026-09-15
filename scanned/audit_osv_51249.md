# [H] CVE-2021-23133

## Summary
Severity: High
Advisory: CVE-2021-23133
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-22
Source: https://osv.dev/vulnerability/CVE-2021-23133
Type: osv

## Details
A race condition in Linux kernel SCTP sockets (net/sctp/socket.c) before 5.12-rc8 can lead to kernel privilege escalation from the context of a network service or an unprivileged process. If sctp_destroy_sock is called without sock_net(sk)->sctp.addr_wq_lock then an element is removed from the auto_asconf_splist list without any proper locking. This can be exploited by an attacker with network service privileges to escalate to root or from the context of an unprivileged user directly if a BPF_CGROUP_INET_SOCK_CREATE is attached which denies creation of some SCTP socket.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XZASHZVCOFJ4VU2I3BN5W5EPHWJQ7QWX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CUX2CA63453G34C6KYVBLJXJXEARZI2X/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PAEQ3H6HKNO6KUCGRZVYSFSAGEUX23JL/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://security.netapp.com/advisory/ntap-20210611-0008/
- http://www.openwall.com/lists/oss-security/2021/05/10/4
- http://www.openwall.com/lists/oss-security/2021/05/10/1
- http://www.openwall.com/lists/oss-security/2021/05/10/3
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b166a20b07382b8bc1dcee2a448715c9c2c81b5b
- https://www.openwall.com/lists/oss-security/2021/04/18/2
- http://www.openwall.com/lists/oss-security/2021/05/10/2
