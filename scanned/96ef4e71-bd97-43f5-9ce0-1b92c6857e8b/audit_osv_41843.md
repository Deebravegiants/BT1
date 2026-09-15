# [H] Bluetooth: l2cap: clear chan->ident on ECRED reconfiguration success

## Summary
Severity: High
Advisory: CVE-2026-63976
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63976
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: l2cap: clear chan->ident on ECRED reconfiguration success

l2cap_ecred_reconf_rsp() returns early on success without clearing
chan->ident. Every other L2CAP response handler (l2cap_ecred_conn_rsp,
l2cap_le_connect_rsp, l2cap_config_rsp) clears chan->ident after a
successful transaction to prevent the channel from matching subsequent
responses with the recycled ident value.

A remote attacker that completed a reconfiguration as the peer can
replay a failure response with the stale ident, causing the kernel to
match and destroy the already-established channel via
l2cap_chan_del(chan, ECONNRESET).

Clear chan->ident for all matching channels on success, and harden the
failure path by using l2cap_chan_hold_unless_zero() consistent with
other L2CAP handlers (l2cap_le_command_rej, __l2cap_get_chan_by_ident).

## References
- https://git.kernel.org/stable/c/00e1950716c6ed67d74777b2db286b0fa23b4be9
- https://git.kernel.org/stable/c/3b5b5f423b4fd23404a393bda8adba3cd6f74ef1
- https://git.kernel.org/stable/c/59f5ecf6ad5c4db6ae81965a96156954a3b0d89a
- https://git.kernel.org/stable/c/8e7977afaef37c6bd2b2654f1bce6ab40d471147
- https://git.kernel.org/stable/c/ae0152d77d101c920769934fb102b18de0c6f526
- https://git.kernel.org/stable/c/c2afd2613fda90107c5e2fe8e855627451749c78
- https://git.kernel.org/stable/c/cc2b4f749de09975bfa06e58bbbad2f6acd4c79c
- https://git.kernel.org/stable/c/f39049304ba655ffcbb92edbdf8c51a1f1210bed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63976.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63976
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
