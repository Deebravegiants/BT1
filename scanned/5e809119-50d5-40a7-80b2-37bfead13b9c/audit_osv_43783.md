# [C] ovpn: skip rehash for peers already removed from by_id

## Summary
Severity: Critical
Advisory: CVE-2026-74727
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74727
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovpn: skip rehash for peers already removed from by_id

ovpn_nl_peer_set_doit() resolves the target peer via
ovpn_peer_get_by_id() before taking ovpn->lock. In the window between
the lookup (which only takes a refcount) and the subsequent
spin_lock_bh(&ovpn->lock), a concurrent OVPN_CMD_PEER_DEL, keepalive
expiry, or socket teardown can take ovpn->lock first, run
ovpn_peer_remove() to unhash the peer from all four tables (by_id,
by_vpn_addr4/6, by_transp_addr) and release the lock. set_doit then
acquires ovpn->lock and calls ovpn_peer_hash_vpn_ip(), which
re-inserts the now-removed peer back into the rehashing tables.

The same race affects the float path: ovpn_peer_endpoints_update()
holds only a refcount and acquires ovpn->lock very late (after async
AEAD decrypt and a netlink notification), then rehashes the peer
in the by_transp_addr table.

The resurrected peer becomes reachable again from the RX lookup
(ovpn_peer_get_by_transp_addr) and the TX VPN-IP lookup, even though
userspace believes it is gone. Once the data-path refcount drops the
peer is freed via call_rcu while the hash entries embedded in it
remain linked, opening a UAF window.

Bail out of the rehash when hash_entry_id is unhashed, mirroring
the sentinel already used by ovpn_peer_remove() to detect the
already-removed state. The check is safe under ovpn->lock, which
serializes every mutation of hash_entry_id, and is a no-op for the
add path because ovpn_peer_add_mp() inserts hash_entry_id before
calling ovpn_peer_hash_vpn_ip().

## References
- https://git.kernel.org/stable/c/33ec10567fe14456063daf549fdf1a4f53448e4c
- https://git.kernel.org/stable/c/66745480298775f188b2f5ad266643e85a90f73b
- https://git.kernel.org/stable/c/d20c181088984b6eaa8d7fe7cb5ab3510988df59
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74727.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74727
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
