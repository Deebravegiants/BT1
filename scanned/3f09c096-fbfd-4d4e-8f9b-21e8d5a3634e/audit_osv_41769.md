# [H] apparmor: mediate the implicit connect of TCP fast open sendmsg

## Summary
Severity: High
Advisory: CVE-2026-63828
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63828
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: mediate the implicit connect of TCP fast open sendmsg

sendmsg()/sendto() with MSG_FASTOPEN is a combination of connect(2) and
write(2): it opens the connection in the SYN. apparmor_socket_sendmsg()
only checks AA_MAY_SEND, so a profile that grants send but denies connect
lets a confined task open an outbound TCP/MPTCP connection that connect(2)
would have refused, bypassing connect mediation.

Mediate the implicit connect when MSG_FASTOPEN is set and a destination
is supplied. Add it to apparmor_socket_sendmsg() (not the shared
aa_sock_msg_perm() helper, which recvmsg also uses) and call aa_sk_perm()
directly, mirroring the selinux and tomoyo fixes. sk_is_tcp() does not
cover MPTCP fast open, so the SOCK_STREAM/IPPROTO_MPTCP arm is explicit.

## References
- https://git.kernel.org/stable/c/07b71c342382b854ab8030b244aeab6a7228ad7d
- https://git.kernel.org/stable/c/20383429b56974507c465d016e5238b189f7a246
- https://git.kernel.org/stable/c/45ebb934ea50b436ce49b2f159f090dab0d7fa28
- https://git.kernel.org/stable/c/4a69b83045d3195d5b9a9b053ad840ddb2998b4e
- https://git.kernel.org/stable/c/4d587cd8a72155089a627130bbd4716ec0856e21
- https://git.kernel.org/stable/c/7f57428ce00891d26b0f087ef754a4d820ec83aa
- https://git.kernel.org/stable/c/a16714e7cf2baa98ba2efddd5d6cbac641f4e76b
- https://git.kernel.org/stable/c/faea60deaa05c76f0772650f42eafde12bd39d93
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63828.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63828
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
