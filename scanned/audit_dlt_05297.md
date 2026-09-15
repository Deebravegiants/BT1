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
before the session, round and member checks, and that verifies against
`signable.index()` — the unit's creator, straight off the wire. This
reaches `Keychain::verify` → `to_peer_id`.
- **`RequestNewest` with an out-of-range requester.**
`Runway::on_request_newest` takes the requester verbatim and addresses
the response to `Recipient::Node(requester)`. `store.newest_unit()`
filters rather than indexes, so it returns `None` instead of erroring
earlier, and the message reaches `Network::send` → `to_peer_id`.

Either way the panic kills an essential task, which tears down the Aleph
session; consensus returns, shuts down its task group, and `fedimintd`
exits. One guardian halts the whole federation.

The fix returns `Option<PeerId>` and handles it where the index arrives:

- `Network::send` drops a message addressed to an index that cannot name
a peer.
- `Keychain::verify` returns `false`; an index that names no peer cannot
have signed anything we accept.

Rejecting these in `Keychain::verify` also fixes an out-of-bounds panic
inside Aleph itself: `bootstrap_multi` does
`NodeMap::with_size(pks.len()).insert(index, ..)`, and `NodeMap::insert`
is a raw `self.0[node_id.0] = ..`. It is only reached from
`into_partially_multisigned` after a successful `check()`, so requiring
the index to be a known peer transitively keeps it in bounds. The same
holds for `is_complete`, which iterates a `NodeMap` whose size the
sender controls.

`FinalizationHandler` deliberately keeps an `expect`. Silently skipping
a finalized unit would make this guardian compute a different session
outcome than its peers — a consensus split, strictly worse than a crash.
The index is unreachable-invalid there because a unit is only finalized
after its creator's signature was verified against the broadcast public
key set.

## Reviewing

Worth being opinionated about the `FinalizationHandler` decision: it is
the one call site that still panics, and the reasoning is that a
divergent session outcome is worse than a halt.

Also worth a look: `to_peer_id` bounds indices to `u16`, not to the
federation's actual peer count. Indices in `n..=u16::MAX` still produce
a `PeerId`, and the downstream lookups reject them (`pks.get` returns
`None`, and `ReconnectP2PConnections::send` warns about a missing
connection). That is sufficient to remove the panic, but if we would
rather reject non-peers up front, `to_peer_id` needs access to the peer
set.

Note the `trace!` level in `Network::send` — a peer can trigger that
line at will, so a louder level would be a log spam vector.

## Testing

Added unit tests covering both fixed call sites:

- `to_peer_id_roundtrips_valid_indices` /
`to_peer_id_rejects_out_of_range_indices` in `consensus::aleph_bft`.
- `verify_rejects_out_of_range_node_index` in
`consensus::aleph_bft::keychain`, which signs a message and asserts that
verification against `NodeIndex(u16::MAX as usize + 1)` and
`NodeIndex(usize::MAX)` returns `false` rather than panicking.

Both keychain and `to_peer_id` tests fail with a panic against the
previous code, so they are genuine regression tests.

`cargo clippy --locked --workspace --all-targets -- -D warnings`, `just
cargo-sort-check` and the pre-commit hook all pass locally.

This branch is based on `master`; the same code is present on
`releases/v0.12` and will need a backport.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01FhzEpwvN4fETvpX6bpmMAD

### fedimint-server/src/consensus/aleph_bft/finalization_handler.rs
```diff
@@ -28,7 +28,13 @@ impl aleph_bft::FinalizationHandler<UnitData> for FinalizationHandler {
         // the channel is unbounded
         self.sender
             .try_send(OrderedUnit {
-                creator: super::to_peer_id(creator),
+                // Skipping a finalized unit would make us compute a different session
+                // outcome than our peers, so we must not swallow an invalid index here.
+                // It is unreachable regardless: a unit is only finalized after its
+                // signature was verified against our broadcast public key set, which
+                // requires its creator to be one of our peers.
+                creator: super::to_peer_id(creator)
+                    .expect("Finalized units were verified against the broadcast public key set"),
                 round,
                 data,
             })
```

### fedimint-server/src/consensus/aleph_bft/keychain.rs
```diff
@@ -97,8 +97,15 @@ impl aleph_bft::Keychain for Keychain {
         signature: &Self::Signature,
         node_index: aleph_bft::NodeIndex,
     ) -> bool {
+        // Aleph verifies signatures before it validates the index they are attributed
+        // to, so this index is chosen by the peer that sent the message. An index that
+        // cannot name a peer cannot have signed anything we accept.
+        let Some(peer_id) = super::to_peer_id(node_index) else {
+            return false;
+        };
+
         match schnorr::Signature::from_slice(signature) {
-            Ok(sig) => self.verify_schnorr(message, &sig, super::to_peer_id(node_index)),
+            Ok(sig) => self.verify_schnorr(message, &sig, peer_id),
             Err(_) => false,
         }
     }
@@ -127,3 +134,45 @@ impl aleph_bft::MultiKeychain for Keychain {
         partial.iter().all(|(i, sgn)| self.verify(msg, sgn, i))
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use std::collections::BTreeMap;
+
+    use aleph_bft::{Keychain as _, NodeIndex};
+    use fedimint_core::encoding::Encodable;
+    use fedimint_core::{PeerId, secp256k1};
+    use secp256k1::{Keypair, SecretKey};
+
+    use super::Keychain;
+
+    fn keychain() -> Keychain {
+        let keypair = Keypair::from_secret_key(
+            secp256k1::SECP256K1,
+            &SecretKey::from_slice(&[1; 32]).expect("Valid secret key"),
+        );
+
+        let pks = BTreeMap::from([(PeerId::from(0), keypair.public_key())]);
+
+        Keychain {
+            identity: PeerId::from(0),
+            message_tag: pks.consensus_hash(),
+            pks,
+            keypair,
+        }
+    }
+
+    #[test]
+    fn verify_rejects_out_of_range_node_index() {
+        let keychain = keychain();
+        let signature = keychain.sign(b"message");
+
+        assert!(keychain.verify(b"message", &signature, NodeIndex(0)));
+
+        // A malicious peer can embed an arbitrary u64 index in a unit it sends us and
+        // aleph-bft verifies the signature before it validates that index, so this must
+        // return false rather than panic and take the consensus session down.
+        assert!(!keychain.verify(b"message", &signature, NodeIndex(usize::from(u16::MAX) + 1)));
+        assert!(!keychain.verify(b"message", &signature, NodeIndex(usize::MAX)));
+    }
+}
```

### fedimint-server/src/consensus/aleph_bft/mod.rs
```diff
@@ -8,12 +8,43 @@ pub mod spawner;
 use aleph_bft::NodeIndex;
 use fedimint_core::PeerId;
 
-pub fn to_peer_id(node_index: NodeIndex) -> PeerId {
+/// Convert an aleph-bft `NodeIndex` into a `PeerId`, if it can represent one.
+///
+/// `NodeIndex` wraps a `usize` and its decoder accepts any `u64` verbatim, so
+/// every index embedded in a message received from a peer is chosen by that
+/// peer and may not correspond to any peer at all. Callers have to handle
+/// `None` instead of panicking, since a panic in the consensus task shuts down
+/// the entire node.
+pub fn to_peer_id(node_index: NodeIndex) -> Option<PeerId> {
     u16::try_from(usize::from(node_index))
-        .expect("The node index corresponds to a valid PeerId")
-        .into()
+        .ok()
+        .map(PeerId::from)
 }
 
 pub fn to_node_index(peer_id: PeerId) -> NodeIndex {
     usize::from(u16::from(peer_id)).into()
 }
+
+#[cfg(test)]
+mod tests {
+    use aleph_bft::NodeIndex;
+    use fedimint_core::PeerId;
+
+    use super::{to_node_index, to_peer_id};
+
+    #[test]
+    fn to_peer_id_roundtrips_valid_indices() {
+        for peer_id in [PeerId::from(0), PeerId::from(3), PeerId::from(u16::MAX)] {
+            assert_eq!(to_peer_id(to_node_index(peer_id)), Some(peer_id));
+        }
+    }
+
+    #[test]
+    fn to_peer_id_rejects_out_of_range_indices() {
+        // A malicious peer can embed an arbitrary u64 in a message it sends us, so
+        // this must not panic and take the consensus session down with it.
+        for index in [usize::from(u16::MAX) + 1, u32::MAX as usize, usize::MAX] {
+            assert_eq!(to_peer_id(NodeIndex(index)), None);
+        }
+    }
+}
```

### fedimint-server/src/consensus/aleph_bft/network.rs
```diff
@@ -12,7 +12,7 @@ use fedimint_core::session_outcome::SignedSessionOutcome;
 use fedimint_core::util::FmtCompact as _;
 use fedimint_logging::LOG_CONSENSUS;
 use parity_scale_codec::{Decode, Encode, IoReader};
-use tracing::error;
+use tracing::{error, trace};
 
 use super::super::db::SignedSessionOutcomeKey;
 use super::data_provider::UnitData;
@@ -65,7 +65,19 @@ impl aleph_bft::Network<NetworkData> for Network {
         // convert from aleph_bft::Recipient to session::Recipient
         let recipient = match recipient {
             aleph_bft::Recipient::Node(node_index) => {
-                Recipient::Peer(super::to_peer_id(node_index))
+                // Aleph echoes back node indices taken from messages we received, so this
+                // index may have been chosen by a peer and may not name a peer at all.
+                let Some(peer_id) = super::to_peer_id(node_index) else {
+                    trace!(
+                        target: LOG_CONSENSUS,
+                        ?node_index,
+                        "Dropping Aleph BFT message addressed to an invalid node index"
+                    );
+
+                    return;
+                };
+
+                Recipient::Peer(peer_id)
             }
             aleph_bft::Recipient::Everyone => Recipient::Everyone,
         };
```
