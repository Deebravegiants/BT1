# [?] Merge pull request #3508 from peilun-conflux/fix/pos-vrf-proposal-panic

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-05-25
Source: https://github.com/Conflux-Chain/conflux-rust/commit/c76eb84bd38dd714607e672f59258f33d5df69f6
Type: security-commit

## Details
Merge pull request #3508 from peilun-conflux/fix/pos-vrf-proposal-panic

fix: reject PoS proposals missing vrf proof instead of panicking

## Patch
### crates/cfxcore/core/src/pos/consensus/liveness/vrf_proposer_election.rs
```diff
@@ -103,15 +103,19 @@ impl ProposerElection for VrfProposer {
     }
 
     fn is_valid_proposal(&self, block: &Block) -> bool {
-        let voting_power = match self
-            .epoch_state
-            .verifier()
-            .get_voting_power(&block.author().expect("checked"))
-        {
+        let author = match block.author() {
+            Some(author) => author,
             None => return false,
-            Some(p) => p,
         };
-        let nonce = block.vrf_nonce().expect("checked");
+        let voting_power =
+            match self.epoch_state.verifier().get_voting_power(&author) {
+                None => return false,
+                Some(p) => p,
+            };
+        let (nonce, vrf_proof) = match (block.vrf_nonce(), block.vrf_proof()) {
+            (Some(nonce), Some(vrf_proof)) => (nonce, vrf_proof),
+            _ => return false,
+        };
         if nonce > voting_power || *self.current_round.lock() != block.round() {
             return false;
         }
@@ -121,14 +125,10 @@ impl ProposerElection for VrfProposer {
         let vrf_hash = match self
             .epoch_state
             .verifier()
-            .get_vrf_public_key(&block.author().expect("checked"))
+            .get_vrf_public_key(&author)
         {
             Some(Some(vrf_public_key)) => {
-                match block
-                    .vrf_proof()
-                    .unwrap()
-                    .verify(seed.as_slice(), &vrf_public_key)
-                {
+                match vrf_proof.verify(seed.as_slice(), &vrf_public_key) {
                     Ok(vrf_hash) => vrf_hash,
                     Err(e) => {
                         diem_debug!("is_valid_proposal: invalid proposal err={:?}, block={:?}", e, block);
@@ -156,7 +156,6 @@ impl ProposerElection for VrfProposer {
     fn receive_proposal_candidate(
         &self, block: &Block,
     ) -> anyhow::Result<bool> {
-        // Proposal validity should have been checked in `process_proposal`.
         let current_round = *self.current_round.lock();
         if block.round() < current_round {
             anyhow::bail!("Incorrect round");
@@ -166,14 +165,14 @@ impl ProposerElection for VrfProposer {
             // sync_up.
             return Ok(true);
         }
+        // `block` is not yet verified on the `filter_proposal` path.
+        let block_vrf_number = self.get_vrf_number(block).ok_or_else(|| {
+            anyhow::anyhow!("proposal missing vrf proof/nonce")
+        })?;
         let old_proposal = self.proposal_candidates.lock();
-        if old_proposal.is_none()
-            || self.get_vrf_number(old_proposal.as_ref().unwrap()).unwrap()
-                > self.get_vrf_number(block).unwrap()
-        {
-            Ok(true)
-        } else {
-            Ok(false)
+        match old_proposal.as_ref().and_then(|b| self.get_vrf_number(b)) {
+            Some(old_vrf_number) => Ok(old_vrf_number > block_vrf_number),
+            None => Ok(true),
         }
     }
 
```
