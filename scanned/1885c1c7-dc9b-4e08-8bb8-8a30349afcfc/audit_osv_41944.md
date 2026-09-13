# [H] smb: client: require net admin for CIFS SWN netlink

## Summary
Severity: High
Advisory: CVE-2026-64137
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64137
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: require net admin for CIFS SWN netlink

CIFS_GENL_CMD_SWN_NOTIFY is the userspace witness-notify command.  The
intended sender is the cifs.witness helper, but the generic-netlink
operation currently has no capability flag, so any local process can send
RESOURCE_CHANGE or CLIENT_MOVE notifications to the in-kernel witness
handler.

The same family exposes CIFS_GENL_MCGRP_SWN without multicast-group
capability flags.  Register messages sent to that group include the witness
registration id and, for NTLM-authenticated mounts, the username, domain,
and password attributes copied from the CIFS session.  An unprivileged
local process should not be able to join that group and receive those
messages.

Require CAP_NET_ADMIN for incoming SWN_NOTIFY commands with
GENL_ADMIN_PERM, and require CAP_NET_ADMIN over the network namespace for
joining the SWN multicast group with GENL_MCAST_CAP_NET_ADMIN.  The
cifs.witness service runs with the privileges needed for both operations.

## References
- https://git.kernel.org/stable/c/969bc6370334a5b4720c5470783295d6484bbc95
- https://git.kernel.org/stable/c/9919021a3b7974ae66a5f9915e3a48c10cfd409b
- https://git.kernel.org/stable/c/9cf7eb8919344932f909b2fac76296f7656fda8d
- https://git.kernel.org/stable/c/a3238b09c58f323e40743ce174cd0ab81b5c09ed
- https://git.kernel.org/stable/c/a8d17d22db591099519a89f14dd24810daba74c3
- https://git.kernel.org/stable/c/c2397b93fbb6f44a788fff30f99be2c20cc5e50f
- https://git.kernel.org/stable/c/d1ebfce2c1d161186a82e77590bf7da2ea1bce91
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64137.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64137
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
