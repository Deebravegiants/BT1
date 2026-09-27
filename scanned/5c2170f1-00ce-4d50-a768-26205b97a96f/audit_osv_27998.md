# [H] wireguard: netlink: check for dangling peer via is_dead instead of empty list

## Summary
Severity: High
Advisory: CVE-2024-26951
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26951
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wireguard: netlink: check for dangling peer via is_dead instead of empty list

If all peers are removed via wg_peer_remove_all(), rather than setting
peer_list to empty, the peer is added to a temporary list with a head on
the stack of wg_peer_remove_all(). If a netlink dump is resumed and the
cursored peer is one that has been removed via wg_peer_remove_all(), it
will iterate from that peer and then attempt to dump freed peers.

Fix this by instead checking peer->is_dead, which was explictly created
for this purpose. Also move up the device_update_lock lockdep assertion,
since reading is_dead relies on that.

It can be reproduced by a small script like:

    echo "Setting config..."
    ip link add dev wg0 type wireguard
    wg setconf wg0 /big-config
    (
            while true; do
                    echo "Showing config..."
                    wg showconf wg0 > /dev/null
            done
    ) &
    sleep 4
    wg setconf wg0 <(printf "[Peer]\nPublicKey=$(wg genkey)\n")

Resulting in:

    BUG: KASAN: slab-use-after-free in __lock_acquire+0x182a/0x1b20
    Read of size 8 at addr ffff88811956ec70 by task wg/59
    CPU: 2 PID: 59 Comm: wg Not tainted 6.8.0-rc2-debug+ #5
    Call Trace:
     <TASK>
     dump_stack_lvl+0x47/0x70
     print_address_description.constprop.0+0x2c/0x380
     print_report+0xab/0x250
     kasan_report+0xba/0xf0
     __lock_acquire+0x182a/0x1b20
     lock_acquire+0x191/0x4b0
     down_read+0x80/0x440
     get_peer+0x140/0xcb0
     wg_get_device_dump+0x471/0x1130

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/13d107794304306164481d31ce33f8fdb25a9c04
- https://git.kernel.org/stable/c/302b2dfc013baca3dea7ceda383930d9297d231d
- https://git.kernel.org/stable/c/55b6c738673871c9b0edae05d0c97995c1ff08c4
- https://git.kernel.org/stable/c/710a177f347282eea162aec8712beb1f42d5ad87
- https://git.kernel.org/stable/c/7bedfe4cfa38771840a355970e4437cd52d4046b
- https://git.kernel.org/stable/c/b7cea3a9af0853fdbb1b16633a458f991dde6aac
- https://git.kernel.org/stable/c/f52be46e3e6ecefc2539119784324f0cbc09620a
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26951.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26951
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
