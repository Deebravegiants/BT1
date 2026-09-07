# [H] IPv4-Mapped Mempool Misbehavior Update Aborts Zebra Address Book

## Summary
Severity: High
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-52829
Published: 2026-05-29
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-63wg-wjjj-7cp8
Type: github-advisory

## Details
### Am I affected

You are affected if:

1. You run `zebrad` up to and including `v4.4.1`.
2. Your node listens on the default `[::]` address on a Linux host (the standard deployment configuration — `net.ipv6.bindv6only=0` is the default on all common Linux distributions).
3. Your node is synced near the chain tip (the expected production state for any node participating in the network).

### Summary

An address normalization mismatch between the handshake path and the mempool misbehavior path causes a deterministic assertion panic when a peer connects via IPv4 to a dual-stack IPv6 listener and then triggers a mempool misbehavior penalty.

The handshake path canonicalizes IPv4-mapped IPv6 addresses to plain IPv4 when storing the peer in the address book via `MetaAddr::new_connected`. The mempool misbehavior path forwards the raw transient socket address (IPv4-mapped IPv6 form) when sending `MetaAddrChange::UpdateMisbehavior` to the address book. The address book looks up the canonical IPv4 entry but then asserts that the previous entry's address matches the change's address. The mismatch between the canonical IPv4 address and the raw IPv4-mapped IPv6 address triggers the assertion, and `panic = "abort"` terminates the process.

### Details

On Linux with `net.ipv6.bindv6only=0`, an IPv4 connection accepted by a `[::]` listener is represented internally as an IPv4-mapped IPv6 socket address (e.g., `::ffff:127.0.0.1:8233`). Zebra's `canonical_peer_addr` helper converts these to plain IPv4 (e.g., `127.0.0.1:8233`).

The handshake path uses `MetaAddr::new_connected`, which canonicalizes the address before storing in the address book. However, inbound inventory registration uses `connected_addr.get_transient_addr()`, preserving the raw IPv4-mapped form. When the mempool later downloads an invalid transaction from this peer and generates a misbehavior penalty, the raw transient address is forwarded through the misbehavior channel to `MetaAddrChange::UpdateMisbehavior`, which does not canonicalize.

After the 30-second misbehavior batch flush, `AddressBook::update` retrieves the canonical IPv4 entry but `MetaAddrChange::apply_to_meta_addr` asserts that `previous.addr == self.addr()`, which fails because one is IPv4 and the other is IPv4-mapped IPv6.

The attacker needs only to complete a P2P handshake over IPv4 to a dual-stack listener and advertise an invalid mempool transaction (such as a coinbase transaction). The assertion fires after the 30-second misbehavior batch flush.

### Patches

Patched in Zebra 4.5.0. The fix canonicalizes the address in the misbehavior update path via a new `MetaAddr::new_misbehavior` constructor that applies `canonical_peer_addr` before creating the `UpdateMisbehavior` change.

### Workarounds

Configuring `listen_addr` to an IPv4-only address (e.g., `0.0.0.0:8233`) avoids the IPv4-mapped IPv6 representation and prevents this specific assertion. Alternatively, setting `net.ipv6.bindv6only=1` on Linux prevents dual-stack acceptance.

### Impact

A remote unauthenticated peer can deterministically crash any synced Zebra node running the default Linux dual-stack configuration with a single invalid mempool transaction advertisement, followed by a 30-second wait. The attack requires no mining capability, no RPC access, no funds, and no special privileges. The crash can be repeated after each restart, causing persistent downtime. Linux dual-stack sockets and mempool activation are the default production state, not special preconditions.

### Credit


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-63wg-wjjj-7cp8_
