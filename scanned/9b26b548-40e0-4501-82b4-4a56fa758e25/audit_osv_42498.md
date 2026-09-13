# [H] tipc: fix u16 MTU truncation in media and bearer MTU validation

## Summary
Severity: High
Advisory: CVE-2026-68297
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68297
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: fix u16 MTU truncation in media and bearer MTU validation

Both TIPC_NL_MEDIA_SET and TIPC_NL_BEARER_SET accept user-supplied
MTU values but only enforce a minimum bound, not a maximum. When a user
sets the MTU to a value exceeding U16_MAX (65535), it passes validation
but is silently truncated when assigned to u16 fields l->mtu and
l->advertised_mtu in tipc_link_create(). Values like 65536 (0x10000)
truncate to 0, causing a division by zero in tipc_link_set_queue_limits()
which computes TIPC_MAX_PUBL / (l->mtu / ITEM_SIZE). Other overflowing
values (e.g. 65537-131071) produce small incorrect MTU values, resulting
in link malfunction behaviors.

Crash stack (triggered as unprivileged user via user namespace):

  tipc_link_set_queue_limits  net/tipc/link.c:2531
  tipc_link_create            net/tipc/link.c:520
  tipc_node_check_dest        net/tipc/node.c:1279
  tipc_disc_rcv               net/tipc/discover.c:252
  tipc_rcv                    net/tipc/node.c:2129
  tipc_udp_recv               net/tipc/udp_media.c:392

Two independent paths lack the upper bound check:
1. tipc_udp_mtu_bad() -- called from __tipc_nl_media_set() (MEDIA_SET)
2. inline check in __tipc_nl_bearer_set() at bearer.c:1160 (BEARER_SET)

Fix both by rejecting MTU values above U16_MAX.

## References
- https://git.kernel.org/stable/c/1b8fb5a20508bfb0db854e01214888c761b3a911
- https://git.kernel.org/stable/c/8bfdfe0dbb36a650b7c4dec1aeae078319938a0b
- https://git.kernel.org/stable/c/9f29cd8a8e7901a2617c8064ce9f50fc67b97cb8
- https://git.kernel.org/stable/c/c1cda72f6acec02ebd45d913bf8527ff77336ba6
- https://git.kernel.org/stable/c/dc4b577a083b361d25e118dc96d8281255ebe22c
- https://git.kernel.org/stable/c/dfdfd987f1917c84766e097a6120a1f3f1634940
- https://git.kernel.org/stable/c/f02334a9e378f7e07232b26dc3d2ab353339f040
- https://git.kernel.org/stable/c/f4013598b69457dbea350df52e52daea6faef8eb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68297.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68297
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
