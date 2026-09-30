# [?] fix: reject Byzantine PoS proposals instead of panicking

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-05-27
Source: https://github.com/Conflux-Chain/conflux-rust/commit/2da8ea1ba7949712c43e8375161c993b61afc161
Type: security-commit

## Details
fix: reject Byzantine PoS proposals instead of panicking

Two consensus-liveness panic vectors closed:

1. `TransactionAuthenticator` methods `unreachable!("reserved variant")`
   on the `_ReservedEd25519` / `_ReservedMultiEd25519` BCS-compat unit
   variants. A Byzantine proposer can BCS-decode a block payload into a
   reserved variant; `Block::deserialize` is hand-rolled and bypasses
   the `BlockUnchecked` safety layer, so the bad variant reaches
   `PosVM::execute_block` → `check_signature_for_user_tx` → `verify()` →
   panic on every honest peer applying the malicious block. Return Err
   instead. The sibling `scheme()` / `public_key_bytes()` /
   `signature_bytes()` / `Display` paths are also made panic-free for
   defense-in-depth; `Scheme::ReservedEd25519` / `ReservedMultiEd25519`
   preserve the historic BCS-tag-to-scheme-byte injectivity.

2. `ProposalMsg::proposer()` `.expect()` on `Block::author()`, called
   from `proposal.rs` and `consensus_msg.rs` network handlers BEFORE
   any verification, panics on a Byzantine `block_type: NilBlock`
   proposal — the hand-rolled `Block::deserialize` preserves
   `block_type` and `vrf_nonce_and_proof` independently, so a peer can
   hand-craft one. Change `proposer()` to return `Option<Author>`;
   reject in both network handlers; reorder `ProposalMsg::verify` to
   run `verify_well_formed` first (rejects NilBlock-as-proposal at the
   door so the VRF branch's author check stays safe).

Same defect class as PR #3508 (`fix/pos-vrf-proposal-panic`); single
Byzantine validator can crash all honest peers via one message in
either family. No on-chain state changes; both fixes ship as
unconditional hotfixes — patched and unpatched nodes both decline to
vote, differing only in panic vs. clean error.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### crates/cfxcore/core/src/pos/consensus/round_manager.rs
```diff
@@ -420,11 +420,17 @@ impl RoundManager {
             Err(anyhow::anyhow!("Injected error in process_proposal_msg"))
         });
 
+        let proposer = proposal_msg.proposer().ok_or_else(|| {
+            anyhow::anyhow!(
+                "ProposalMsg without author reached process_proposal_msg \
+                 — verify_well_formed should have rejected it"
+            )
+        })?;
         if self
             .ensure_round_and_sync_up(
                 proposal_msg.proposal().round(),
                 proposal_msg.sync_info(),
-                proposal_msg.proposer(),
+                proposer,
                 true,
             )
             .await
@@ -449,8 +455,7 @@ impl RoundManager {
                 // because we only broadcast a proposal when we receive it for
                 // the first time.
                 // TODO(lpl): Do not send to the sender and the original author.
-                let exclude =
-                    vec![proposal_msg.proposer(), self.network.author];
+                let exclude = vec![proposer, self.network.author];
                 self.network
                     .broadcast(
                         ConsensusMsg::ProposalMsg(Box::new(proposal_msg)),
```

### crates/cfxcore/core/src/pos/protocol/message/consensus_msg.rs
```diff
@@ -9,15 +9,23 @@ use crate::{
     },
     sync::Error,
 };
-use diem_logger::prelude::diem_debug;
+use diem_logger::prelude::{diem_debug, diem_trace};
 use std::mem::discriminant;
 
 impl Handleable for ConsensusMsg {
     fn handle(self, ctx: &Context) -> Result<(), Error> {
         diem_debug!("on_consensus_msg, msg={:?}", &self);
         let peer_address = ctx.get_peer_account_address()?;
+        // Mirror `proposal.rs`'s reject-at-handler policy for authorless
+        // proposals.
         let author = match &self {
-            ConsensusMsg::ProposalMsg(p) => p.proposer(),
+            ConsensusMsg::ProposalMsg(p) => p.proposer().ok_or_else(|| {
+                diem_trace!(
+                    "Dropping authorless proposal from {:?}",
+                    peer_address
+                );
+                Error::InvalidMessageFormat
+            })?,
             ConsensusMsg::VoteMsg(v) => v.vote().author(),
             _ => peer_address,
         };
```

### crates/cfxcore/core/src/pos/protocol/message/proposal.rs
```diff
@@ -11,7 +11,7 @@ use crate::{
 };
 
 use consensus_types::proposal_msg::ProposalMsg;
-use diem_logger::prelude::diem_debug;
+use diem_logger::prelude::{diem_debug, diem_trace};
 use std::mem::discriminant;
 
 impl Handleable for ProposalMsg {
@@ -25,7 +25,12 @@ impl Handleable for ProposalMsg {
             "proposal received must be from the sending peer"
         );*/
 
-        let author = self.proposer();
+        // Drop NilBlock/Genesis-shaped peer proposals: the channel keys
+        // by `(author, discriminant)` so we need a real author here.
+        let author = self.proposer().ok_or_else(|| {
+            diem_trace!("Dropping authorless proposal from {:?}", peer_address);
+            Error::InvalidMessageFormat
+        })?;
         let msg = ConsensusMsg::ProposalMsg(Box::new(self));
         ctx.manager
             .consensus_network_task
```

### crates/pos/consensus/consensus-types/src/proposal_msg.rs
```diff
@@ -85,24 +85,27 @@ impl ProposalMsg {
     pub fn verify(
         &self, validator: &ValidatorVerifier, epoch_vrf_seed: &[u8],
     ) -> Result<()> {
+        // Run well-formedness first: it rejects NilBlock/Genesis and
+        // guarantees `author().is_some()` for the VRF branch below.
+        self.verify_well_formed()?;
         self.proposal
             .validate_signature(validator)
             .map_err(|e| format_err!("{:?}", e))?;
 
         if let Some(vrf_proof) = self.proposal.vrf_proof() {
+            let author = self.proposal.author().ok_or_else(|| {
+                format_err!("VRF proof present but block has no author")
+            })?;
             validator.verify_vrf(
-                self.proposal.author().unwrap(),
+                author,
                 &self.proposal.block_data().vrf_round_seed(epoch_vrf_seed),
                 vrf_proof,
             )?;
         }
-        // if there is a timeout certificate, verify its signatures
         if let Some(tc) = self.sync_info.highest_timeout_certificate() {
             tc.verify(validator).map_err(|e| format_err!("{:?}", e))?;
         }
-        // Note that we postpone the verification of SyncInfo until it's being
-        // used.
-        self.verify_well_formed()
+        Ok(())
     }
 
     pub fn proposal(&self) -> &Block { &self.proposal }
@@ -111,11 +114,9 @@ impl ProposalMsg {
 
     pub fn sync_info(&self) -> &SyncInfo { &self.sync_info }
 
-    pub fn proposer(&self) -> Author {
-        self.proposal
-            .author()
-            .expect("Proposal should be verified having an author")
-    }
+    /// `None` for `NilBlock` / `Genesis`. Peer messages may carry either
+    /// before validation, so we don't panic here.
+    pub fn proposer(&self) -> Option<Author> { self.proposal.author() }
 }
 
 impl fmt::Display for ProposalMsg {
```

### crates/pos/types/types/src/transaction/authenticator.rs
```diff
@@ -6,7 +6,7 @@
 // See http://www.gnu.org/licenses/
 
 use crate::account_address::AccountAddress;
-use anyhow::{ensure, Error, Result};
+use anyhow::{bail, ensure, Error, Result};
 use diem_crypto::{
     bls::{
         BLSPublicKey, BLSPublicKeyUnchecked, BLSSignature,
@@ -40,9 +40,17 @@ use std::{convert::TryFrom, fmt, str::FromStr};
 /// (2).
 
 // TODO: in the future, can tie these to the TransactionAuthenticator enum directly with https://github.com/rust-lang/rust/issues/60553
+//
+// Discriminants must mirror the matching `TransactionAuthenticator` BCS
+// tag — `AuthenticationKeyPreimage::new` appends `scheme as u8`.
 #[derive(Debug)]
 #[repr(u8)]
+#[non_exhaustive]
 pub enum Scheme {
+    /// BCS tag 0 (ex-Ed25519, never used in Conflux PoS).
+    ReservedEd25519 = 0,
+    /// BCS tag 1 (ex-MultiEd25519, never used in Conflux PoS).
+    ReservedMultiEd25519 = 1,
     BLS = 2,
     MultiBLS = 3,
     // ... add more schemes here
@@ -51,6 +59,8 @@ pub enum Scheme {
 impl fmt::Display for Scheme {
     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
         let display = match self {
+            Scheme::ReservedEd25519 => "reserved_ed25519",
+            Scheme::ReservedMultiEd25519 => "reserved_multi_ed25519",
             Scheme::BLS => "bls",
             Scheme::MultiBLS => "multi_bls",
         };
@@ -117,12 +127,11 @@ impl From<TransactionAuthenticatorUnchecked> for TransactionAuthenticator {
 }
 
 impl TransactionAuthenticator {
-    /// Unique identifier for the signature scheme
+    /// Unique identifier for the signature scheme.
     pub fn scheme(&self) -> Scheme {
         match self {
-            Self::_ReservedEd25519 | Self::_ReservedMultiEd25519 => {
-                unreachable!("reserved variant")
-            }
+            Self::_ReservedEd25519 => Scheme::ReservedEd25519,
+            Self::_ReservedMultiEd25519 => Scheme::ReservedMultiEd25519,
             Self::BLS { .. } => Scheme::BLS,
             Self::MultiBLS { .. } => Scheme::MultiBLS,
         }
@@ -140,11 +149,12 @@ impl TransactionAuthenticator {
     }
 
     /// Return Ok if the authenticator's public key matches its signature, Err
-    /// otherwise
+    /// otherwise. Reserved variants always return Err (Byzantine input
+    /// must not crash the executor).
     pub fn verify<T: Serialize + CryptoHash>(&self, message: &T) -> Result<()> {
         match self {
             Self::_ReservedEd25519 | Self::_ReservedMultiEd25519 => {
-                unreachable!("reserved variant")
+                bail!("reserved authenticator variant has no signature")
             }
             Self::BLS {
                 public_key,
@@ -157,25 +167,23 @@ impl TransactionAuthenticator {
         }
     }
 
-    /// Return the raw bytes of `self.public_key`
+    /// Return the raw bytes of `self.public_key`. MultiBLS has no per-tx
+    /// pubkey (the verifying set lives on the committee); Reserved
+    /// variants have no signature material at all.
     pub fn public_key_bytes(&self) -> Vec<u8> {
         match self {
-            Self::_ReservedEd25519 | Self::_ReservedMultiEd25519 => {
-                unreachable!("reserved variant")
-            }
+            Self::_ReservedEd25519 | Self::_ReservedMultiEd25519 => Vec::new(),
             Self::BLS { public_key, .. } => public_key.to_bytes().to_vec(),
-            Self::MultiBLS { .. } => todo!(),
+            Self::MultiBLS { .. } => Vec::new(),
         }
     }
 
     /// Return the raw bytes of `self.signature`
     pub fn signature_bytes(&self) -> Vec<u8> {
         match self {
-            Self::_ReservedEd25519 | Self::_ReservedMultiEd25519 => {
-                unreachable!("reserved variant")
-            }
+            Self::_ReservedEd25519 | Self::_ReservedMultiEd25519 => Vec::new(),
             Self::BLS { signature, .. } => signature.to_bytes().to_vec(),
-            Self::MultiBLS { .. } => todo!(),
+            Self::MultiBLS { signature } => signature.to_bytes(),
         }
     }
 
@@ -339,11 +347,58 @@ impl fmt::Display for AuthenticationKey {
 
 #[cfg(test)]
 mod tests {
-    use crate::transaction::authenticator::AuthenticationKey;
+    use super::{Scheme, TransactionAuthenticator};
+    use crate::{
+        account_address::AccountAddress,
+        transaction::{
+            authenticator::AuthenticationKey, RawTransaction, RetirePayload,
+        },
+    };
     use std::str::FromStr;
 
     #[test]
     fn test_from_str_should_not_panic_by_given_empty_string() {
         assert!(AuthenticationKey::from_str("").is_err());
     }
+
+    // Regression: a Byzantine PoS proposer can BCS-decode a block
+    // payload into a `_Reserved*` variant; `verify()` must Err, not
+    // panic.
+    #[test]
+    fn reserved_authenticator_verify_returns_err_not_panic() {
+        let raw_txn = RawTransaction::new_retire(
+            AccountAddress::ZERO,
+            RetirePayload {
+                node_id: AccountAddress::ZERO,
+                votes: 0,
+            },
+        );
+
+        for auth in [
+            TransactionAuthenticator::_ReservedEd25519,
+            TransactionAuthenticator::_ReservedMultiEd25519,
+        ] {
+            let err = auth.verify(&raw_txn).unwrap_err();
+            assert!(
+                err.to_string().contains("reserved"),
+                "expected 'reserved' in error, got: {}",
+                err,
+            );
+        }
+    }
+
+    #[test]
+    fn reserved_authenticator_accessors_are_panic_free() {
+        let auth_a = TransactionAuthenticator::_ReservedEd25519;
+        let auth_b = TransactionAuthenticator::_ReservedMultiEd25519;
+
+        // Distinct scheme bytes keep preimages distinct across variants.
+        assert!(matches!(auth_a.scheme(), Scheme::ReservedEd25519));
+        assert!(matches!(auth_b.scheme(), Scheme::ReservedMultiEd25519));
+        assert_ne!(auth_a.scheme() as u8, auth_b.scheme() as u8);
+        assert!(auth_a.public_key_bytes().is_empty());
+        assert!(auth_a.signature_bytes().is_empty());
+        assert!(auth_b.public_key_bytes().is_empty());
+        assert!(auth_b.signature_bytes().is_empty());
+    }
 }
```
