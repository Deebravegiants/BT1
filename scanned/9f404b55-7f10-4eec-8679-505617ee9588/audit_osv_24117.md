# [H] sctp: handle the error returned from sctp_auth_asoc_init_active_key

## Summary
Severity: High
Advisory: CVE-2022-50243
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50243
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.262, >=4.20.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.14.0 <5.19.17, >=5.16.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: handle the error returned from sctp_auth_asoc_init_active_key

When it returns an error from sctp_auth_asoc_init_active_key(), the
active_key is actually not updated. The old sh_key will be freeed
while it's still used as active key in asoc. Then an use-after-free
will be triggered when sending patckets, as found by syzbot:

  sctp_auth_shkey_hold+0x22/0xa0 net/sctp/auth.c:112
  sctp_set_owner_w net/sctp/socket.c:132 [inline]
  sctp_sendmsg_to_asoc+0xbd5/0x1a20 net/sctp/socket.c:1863
  sctp_sendmsg+0x1053/0x1d50 net/sctp/socket.c:2025
  inet_sendmsg+0x99/0xe0 net/ipv4/af_inet.c:819
  sock_sendmsg_nosec net/socket.c:714 [inline]
  sock_sendmsg+0xcf/0x120 net/socket.c:734

This patch is to fix it by not replacing the sh_key when it returns
errors from sctp_auth_asoc_init_active_key() in sctp_auth_set_key().
For sctp_auth_set_active_key(), old active_key_id will be set back
to asoc->active_key_id when the same thing happens.

## References
- https://git.kernel.org/stable/c/022152aaebe116a25c39818a07e175a8cd3c1e11
- https://git.kernel.org/stable/c/0f90099d18e3abdc01babf686f41f63fe04939c1
- https://git.kernel.org/stable/c/19d636b663e0e92951bba5fced929ca7fd25c552
- https://git.kernel.org/stable/c/382ff44716603a54f5fd238ddec6a2468e217612
- https://git.kernel.org/stable/c/3b0fcf5e29c0940e1169ce9c44f73edd98bdf12d
- https://git.kernel.org/stable/c/b8fa99a3a11bdd77fef6b4a97f1021eb30b5ba40
- https://git.kernel.org/stable/c/f65955340e0044f5c41ac799a01698ac7dee8a4e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50243.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50243
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
