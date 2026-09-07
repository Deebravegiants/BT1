# [?] fix(server): do not panic on peer-supplied aleph node indices (#8893)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-07-28
Source: https://github.com/fedimint/fedimint/commit/60fc6d9dd73383ec92f6016a1ac62a92ea999c2a
Type: security-commit

## Details
fix(server): do not panic on peer-supplied aleph node indices (#8893)

## Summary

A malicious guardian can crash every other guardian in its federation
with a single P2P message, by embedding an out-of-range `NodeIndex` in
an Aleph BFT message. This makes `to_peer_id` fallible and handles the
failure at each call site instead of panicking.

## Details

`aleph_bft::NodeIndex` wraps a `usize`, and its scale decoder reads 8
bytes and accepts the result verbatim:

```rust
// aleph-bft-crypto/src/node.rs
impl Decode for NodeIndex {
    fn decode<I: Input>(value: &mut I) -> Result<Self, Error> {
        let mut arr = [0u8; 8];
        value.read(&mut arr)?;
        let val: u64 = u64::from_le_bytes(arr);
        Ok(NodeIndex(val as usize))
    }
}
```

So every node index embedded in a message we receive is chosen by the
sender and need not name a peer. `to_peer_id` converted one with
`.expect("The node index corresponds to a valid PeerId")`. We
authenticate the P2P connection, but that authenticated `peer_id` is
dropped when the decoded payload is handed to Aleph, so nothing binds an
embedded index to the sender.

Two paths reached the `expect` with no forged signature, special
configuration or prior state required:

- **`NewUnit` with an out-of-range `creator`.**
`Validator::validate_unit` calls `uu.check(&self.keychain)` first,

_Trimmed to 38 lines — full report: https://github.com/fedimint/fedimint/commit/60fc6d9dd73383ec92f6016a1ac62a92ea999c2a_
