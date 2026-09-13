# [?] [consensus] Harden SecretShare ingress validation against DoS (#19475)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-04-18
Source: https://github.com/aptos-labs/aptos-core/commit/b4ca925a9e657868dc6a1cceaeef3c70c036e6b1
Type: security-commit

## Details
[consensus] Harden SecretShare ingress validation against DoS (#19475)

* [crypto] Make weighted config player lookups fallible

Return Result instead of panicking on out-of-bounds player ids in
get_virtual_player, get_player_weight, and get_all_virtual_players.
Callers that operate on remotely-authored input (e.g. PVSS verify,
reconstruct) can now bubble up a typed error instead of aborting
the process.

Also add defensive length and bounds checks in the weighted
Reconstructable impls so that a malformed share vector is rejected
before indexing the virtual-player space.

All internal DKG call sites that iterate over trusted player ids
derived from sc.get_player(i) retain the invariant via .expect,
keeping the change footprint small for the existing trait surface.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>

* [consensus] Validate SecretShare structure before crypto verification

A malicious validator could send a SecretShare with a share vector
shorter than its author's expected weight, or with a player id that
does not match the author's validator index. Prior to this change
the optimistic-verification fast path accepted such shares and
relied on a later panicking index into the virtual-player space,
which crashed the node from inside spawn_blocking.

verify_structural now checks:
- share.share.0.id matches the author's validator index
- share.share.1.len() equals the author's expected weight

before deferring to the (expensive) cryptographic verification.
Tests cover shorter-than-expected and longer-than-expected vectors,
player-id mismatch, and author-mismatch. A regression test in the
share store bypasses verify_structural to exercise the downstream
defense-in-depth path in reconstruct.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.7 <noreply@anthropic.com>

### consensus/src/rand/rand_gen/types.rs
```diff
@@ -697,7 +697,9 @@ impl RandConfig {
         let player = Player {
             id: self.get_id(peer),
         };
-        self.wconfig.get_player_weight(&player) as u64
+        self.wconfig
+            .get_player_weight(&player)
+            .expect("peer's player id is in bounds") as u64
     }
 
     pub fn threshold(&self) -> u64 {
```

### consensus/src/rand/secret_sharing/secret_share_store.rs
```diff
@@ -836,6 +836,47 @@ mod tests {
         }
     }
 
+    #[tokio::test]
+    async fn test_store_aggregation_with_malformed_vector_share() {
+        // Defense-in-depth: if a share with the wrong vector length somehow bypasses
+        // structural checks and reaches aggregation, reconstruction must return an
+        // error rather than panic (which would crash the node).
+        let ctx = TestContext::new(vec![1, 2, 2, 1]);
+        let (mut store, mut rx) = make_store(&ctx);
+        let round = 5;
+        store.update_highest_known_round(round);
+        let metadata = create_metadata(ctx.epoch, round);
+
+        // self share (weight 1)
+        let self_share = create_secret_share(&ctx, 0, &metadata);
+        store.add_self_share(self_share).unwrap();
+
+        // good peer shares (weight 2 and 2) -- total weight 5 == threshold
+        for i in 1..=2 {
+            let share = create_secret_share(&ctx, i, &metadata);
+            store.add_share(share).unwrap();
+        }
+
+        // Malformed share from author[3] (weight 1 but length 3). Pushed in past the
+        // verifier, which in production catches this at optimistic_verify.
+        let mut malformed = create_secret_share(&ctx, 3, &metadata);
+        let extra = malformed.share.1[0].clone();
+        malformed.share.1.push(extra.clone());
+        malformed.share.1.push(extra);
+        store.add_share(malformed).unwrap();
+
+        // Without the defense-in-depth fix to `get_virtual_player`, reconstruct would
+        // panic inside spawn_blocking and this timeout would fire.
+        use futures::StreamExt;
+        let result = tokio::time::timeout(std::time::Duration::from_secs(5), rx.next())
+            .await
+            .expect("Timed out waiting for aggregation result (panic inside spawn_blocking?)")
+            .expect("Channel closed unexpectedly");
+        // Threshold is 5 and weights [1,2,2] after evicting the bad share sum to 5,
+        // so aggregation succeeds on the retry.
+        assert_eq!(unwrap_success(result).metadata, metadata);
+    }
+
     #[tokio::test]
     async fn test_store_failure_recovery_with_new_share() {
         // 3 validators, weights [1,1,1], threshold = 3
```

### consensus/src/rand/secret_sharing/verifier.rs
```diff
@@ -36,8 +36,30 @@ impl SecretShareVerifier {
         self.pessimistic_set.insert(author);
     }
 
-    fn verify_structural(&self, author: &Author) -> anyhow::Result<()> {
-        let _index = self.config.get_id(author)?;
+    fn verify_structural(&self, share: &SecretShare) -> anyhow::Result<()> {
+        let author = share.author();
+        let index = self.config.get_id(author)?;
+        // The Player id embedded in the share must match the author's validator index.
+        // Without this check a malicious validator could declare any player id, leading
+        // to incorrect reconstruction or out-of-bounds access during aggregation.
+        ensure!(
+            share.share.0.id == index,
+            "Player id {} does not match expected index {} for author {}",
+            share.share.0.id,
+            index,
+            author
+        );
+        // The number of sub-shares must equal the author's weight. Without this check a
+        // malicious validator could cause `get_virtual_player` to be called with an
+        // out-of-range index during reconstruction and crash the node.
+        let expected_weight = self.config.get_peer_weight(author)? as usize;
+        ensure!(
+            share.share.1.len() == expected_weight,
+            "Share vector length {} does not match expected weight {} for author {}",
+            share.share.1.len(),
+            expected_weight,
+            author
+        );
         Ok(())
     }
 
@@ -48,8 +70,13 @@ impl SecretShareVerifier {
             share.author(),
             sender
         );
+        // Structural validation runs on both branches: the pessimistic crypto
+        // verify does not bind share.share.0.id to the author's validator
+        // index, so an author could otherwise smuggle a mismatched player id
+        // past verification and poison Lagrange interpolation downstream.
+        self.verify_structural(share)?;
         if self.should_verify_optimistically(share.author()) {
-            self.verify_structural(share.author())
+            Ok(())
         } else {
             share.verify(&self.config)
         }
@@ -115,18 +142,82 @@ mod tests {
     }
 
     #[test]
-    fn test_verify_structural_valid_author() {
+    fn test_verify_structural_valid_share() {
         let ctx = TestContext::new(vec![1, 1, 1, 1]);
         let verifier = SecretShareVerifier::new(ctx.secret_share_config.clone(), true);
-        assert!(verifier.verify_structural(&ctx.authors[0]).is_ok());
+        let metadata = create_metadata(ctx.epoch, 5);
+        let share = create_secret_share(&ctx, 0, &metadata);
+        assert!(verifier.verify_structural(&share).is_ok());
     }
 
     #[test]
     fn test_verify_structural_invalid_author() {
         let ctx = TestContext::new(vec![1, 1, 1, 1]);
         let verifier = SecretShareVerifier::new(ctx.secret_share_config.clone(), true);
-        let unknown = Author::random();
-        assert!(verifier.verify_structural(&unknown).is_err());
+        let metadata = create_metadata(ctx.epoch, 5);
+        let mut share = create_secret_share(&ctx, 0, &metadata);
+        share.author = Author::random();
+        assert!(verifier.verify_structural(&share).is_err());
+    }
+
+    #[test]
+    fn test_verify_structural_rejects_wrong_vector_length() {
+        // authors[1] has weight 2 -- a share with 3 sub-shares must be rejected
+        let ctx = TestContext::new(vec![1, 2, 2, 1]);
+        let verifier = SecretShareVerifier::new(ctx.secret_share_config.clone(), true);
+        let metadata = create_metadata(ctx.epoch, 5);
+        let mut share = create_secret_share(&ctx, 1, &metadata);
+        let extra = share.share.1[0].clone();
+        share.share.1.push(extra);
+        assert_eq!(share.share.1.len(), 3);
+        let err = verifier.verify_structural(&share).unwrap_err();
+        assert!(
+            format!("{err}").contains("Share vector length"),
+            "unexpected error: {err}"
+        );
+    }
+
+    #[test]
+    fn test_verify_structural_rejects_shorter_vector_length() {
+        // authors[1] has weight 2 -- a share with 1 sub-share must be rejected
+        let ctx = TestContext::new(vec![1, 2, 2, 1]);
+        let verifier = SecretShareVerifier::new(ctx.secret_share_config.clone(), true);
+        let metadata = create_metadata(ctx.epoch, 5);
+        let mut share = create_secret_share(&ctx, 1, &metadata);
+        share.share.1.pop();
+        assert_eq!(share.share.1.len(), 1);
+        let err = verifier.verify_structural(&share).unwrap_err();
+        assert!(
+            format!("{err}").contains("Share vector length"),
+            "unexpected error: {err}"
+        );
+    }
+
+    #[test]
+    fn test_verify_structural_rejects_wrong_player_id() {
+        let ctx = TestContext::new(vec![1, 1, 1, 1]);
+        let verifier = SecretShareVerifier::new(ctx.secret_share_config.clone(), true);
+        let metadata = create_metadata(ctx.epoch, 5);
+        let mut share = create_secret_share(&ctx, 1, &metadata);
+        // Flip the player id to a different validator's index
+        share.share.0.id = (share.share.0.id + 1) % 4;
+        let err = verifier.verify_structural(&share).unwrap_err();
+        assert!(
+            format!("{err}").contains("Player id"),
+            "unexpected error: {err}"
+        );
+    }
+
+    #[test]
+    fn test_optimistic_verify_rejects_wrong_vector_length() {
+        let ctx = TestContext::new(vec![1, 2, 2, 1]);
+        let verifier = SecretShareVerifier::new(ctx.secret_share_config.clone(), true);
+        let metadata = create_metadata(ctx.epoch, 5);
+        let mut share = create_secret_share(&ctx, 1, &metadata);
+        let extra = share.share.1[0].clone();
+        share.share.1.push(extra);
+        // author[1] is in the optimistic set so only verify_structural runs
+        assert!(verifier.optimistic_verify(&share, &ctx.authors[1]).is_err());
     }
 
     #[test]
```

### crates/aptos-batch-encryption/src/schemes/fptx_weighted.rs
```diff
@@ -71,7 +71,12 @@ impl WeightedBIBEMasterSecretKeyShare {
         &self,
         tc: &WeightedConfigArkworks<Fr>,
     ) -> Vec<BIBEMasterSecretKeyShare> {
+        // TODO: propagate Result so a deserialized weighted_player with an
+        // out-of-bounds id cannot panic. Safe today because instances are
+        // only constructed locally via FPTXWeighted::setup, not decoded from
+        // untrusted input.
         tc.get_all_virtual_players(&self.weighted_player)
+            .expect("weighted_player id is in bounds")
             .into_iter()
             .enumerate()
             .map(|(i, virt_player)| BIBEMasterSecretKeyShare {
@@ -135,7 +140,12 @@ impl WeightedBIBEVerificationKey {
     }
 
     pub fn virtualized_vks(&self, tc: &WeightedConfigArkworks<Fr>) -> Vec<BIBEVerificationKey> {
+        // TODO: propagate Result so a deserialized weighted_player with an
+        // out-of-bounds id cannot panic. Safe today because instances are
+        // only constructed locally via FPTXWeighted::setup, not decoded from
+        // untrusted input.
         tc.get_all_virtual_players(&self.weighted_player)
+            .expect("weighted_player id is in bounds")
             .into_iter()
             .enumerate()
             .map(|(i, virt_player)| BIBEVerificationKey {
```

### crates/aptos-crypto/src/weighted_config.rs
```diff
@@ -15,10 +15,9 @@ use crate::{
     player::Player,
     traits::{self, TSecretSharingConfig as _, ThresholdConfig},
 };
-use anyhow::anyhow;
+use anyhow::{anyhow, ensure};
 use ark_ec::CurveGroup;
 use ark_ff::FftField;
-use more_asserts::assert_lt;
 use rand::Rng;
 use rand_core::{CryptoRng, RngCore};
 use serde::{Deserialize, Serialize};
@@ -160,8 +159,16 @@ impl<TC: ThresholdConfig> WeightedConfig<TC> {
     }
 
     /// Returns the weight of a specific player.
-    pub fn get_player_weight(&self, player: &Player) -> usize {
-        self.weights[player.id]
+    ///
+    /// Returns an error if `player.id` is out of bounds.
+    pub fn get_player_weight(&self, player: &Player) -> anyhow::Result<usize> {
+        self.weights.get(player.id).copied().ok_or_else(|| {
+            anyhow!(
+                "get_player_weight: player id {} out of bounds (num_players={})",
+                player.id,
+                self.num_players
+            )
+        })
     }
 
     /// Returns the starting index of a player's shares in the flattened vector of all weighted shares.
@@ -174,22 +181,43 @@ impl<TC: ThresholdConfig> WeightedConfig<TC> {
     /// share per "virtual player."
     ///
     /// This function returns the "virtual" player associated with the $i$th sub-share of this player.
-    pub fn get_virtual_player(&self, player: &Player, j: usize) -> Player {
-        // println!("WeightedConfig::get_virtual_player({player}, {i})");
-        assert_lt!(j, self.weights[player.id]);
-
-        let id = self.get_share_index(player.id, j).unwrap();
-
-        Player { id }
+    ///
+    /// Returns an error if `player.id` is out of bounds or if `j` is greater than
+    /// or equal to `player`'s weight. This makes the function safe to call with
+    /// untrusted input (e.g. attacker-controlled `Player` ids or share vector
+    /// lengths) without panicking the process.
+    pub fn get_virtual_player(&self, player: &Player, j: usize) -> anyhow::Result<Player> {
+        let weight = self.weights.get(player.id).copied().ok_or_else(|| {
+            anyhow!(
+                "get_virtual_player: player id {} out of bounds (num_players={})",
+                player.id,
+                self.num_players
+            )
+        })?;
+        ensure!(
+            j < weight,
+            "get_virtual_player: share index {} out of bounds for player {} (weight={})",
+            j,
+            player.id,
+            weight
+        );
+        Ok(Player {
+            id: self.starting_index[player.id] + j,
+        })
     }
 
     /// Returns all "virtual" players corresponding to a given player based on their weight.
-    pub fn get_all_virtual_players(&self, player: &Player) -> Vec<Player> {
-        let w = self.get_player_weight(player);
-
-        (0..w)
-            .map(|i| self.get_virtual_player(player, i))
-            .collect::<Vec<Player>>()
+    ///
+    /// Returns an error if `player.id` is out of bounds.
+    pub fn get_all_virtual_players(&self, player: &Player) -> anyhow::Result<Vec<Player>> {
+        let w = self.get_player_weight(player)?;
+
+        Ok((0..w)
+            .map(|i| {
+                self.get_virtual_player(player, i)
+                    .expect("j < weight holds by construction")
+            })
+            .collect::<Vec<Player>>())
     }
 
     /// `i` is the player's index, from 0 to `self.tc.n`
@@ -280,6 +308,7 @@ impl<TC: ThresholdConfig> WeightedConfig<TC> {
             .into_iter()
             .map(|player| {
                 self.get_all_virtual_players(&player)
+                    .expect("player is from get_players() so id is in bounds")
                     .into_iter()
                     .map(|virt_player| items[virt_player.get_id()].clone())
                     .collect::<Vec<T>>()
@@ -389,8 +418,16 @@ impl<SK: Reconstructable<ThresholdConfigBlstrs>> Reconstructable<WeightedConfigB
             //     "Flattening {} share(s) for player {player}",
             //     sub_shares.len()
             // );
+            let expected_weight = sc.get_player_weight(player)?;
+            ensure!(
+                sub_shares.len() == expected_weight,
+                "reconstruct: player {} has {} sub-shares but expected weight {}",
+                player.id,
+                sub_shares.len(),
+                expected_weight
+            );
             for (pos, share) in sub_shares.iter().enumerate() {
-                let virtual_player = sc.get_virtual_player(player, pos);
+                let virtual_player = sc.get_virtual_player(player, pos)?;
 
                 // println!(
                 //     " + Adding share {pos} as virtual player {virtual_player}: {:?}",
@@ -425,8 +462,16 @@ impl<F: FftField, SK: Reconstructable<ShamirThresholdConfig<F>>>
             //     "Flattening {} share(s) for player {player}",
             //     sub_shares.len()
             // );
+            let expected_weight = sc.get_player_weight(player)?;
+            ensure!(
+                sub_shares.len() == expected_weight,
+                "reconstruct: player {} has {} sub-shares but expected weight {}",
+                player.id,
+                sub_shares.len(),
+                expected_weight
+            );
             for (pos, share) in sub_shares.iter().enumerate() {
-                let virtual_player = sc.get_virtual_player(player, pos);
+                let virtual_player = sc.get_virtual_player(player, pos)?;
 
                 // println!(
                 //     " + Adding share {pos} as virtual player {virtual_player}: {:?}",
@@ -453,22 +498,22 @@ mod test {
         let wc = WeightedConfigBlstrs::new(1, vec![1]).unwrap();
         assert_eq!(wc.starting_index.len(), 1);
         assert_eq!(wc.starting_index[0], 0);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(0), 0).id, 0);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(0), 0).unwrap().id, 0);
 
         // 1-out-of-2, weights 2
         let wc = WeightedConfigBlstrs::new(1, vec![2]).unwrap();
         assert_eq!(wc.starting_index.len(), 1);
         assert_eq!(wc.starting_index[0], 0);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(0), 0).id, 0);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(0), 1).id, 1);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(0), 0).unwrap().id, 0);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(0), 1).unwrap().id, 1);
 
         // 1-out-of-2, weights 1, 1
         let wc = WeightedConfigBlstrs::new(1, vec![1, 1]).unwrap();
         assert_eq!(wc.starting_index.len(), 2);
         assert_eq!(wc.starting_index[0], 0);
         assert_eq!(wc.starting_index[1], 1);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(0), 0).id, 0);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(1), 0).id, 1);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(0), 0).unwrap().id, 0);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(1), 0).unwrap().id, 1);
 
         // 3-out-of-5, some weights are 0.
         let wc = WeightedConfigBlstrs::new(1, vec![0, 0, 0, 2, 2, 2, 0, 0, 0, 3, 3, 3, 0, 0, 0])
@@ -477,20 +522,47 @@ mod test {
             vec![0, 0, 0, 0, 2, 4, 6, 6, 6, 6, 9, 12, 15, 15, 15],
             wc.starting_index
         );
-        assert_eq!(wc.get_virtual_player(&wc.get_player(3), 0).id, 0);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(3), 1).id, 1);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(4), 0).id, 2);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(4), 1).id, 3);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(5), 0).id, 4);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(5), 1).id, 5);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(9), 0).id, 6);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(9), 1).id, 7);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(9), 2).id, 8);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(10), 0).id, 9);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(10), 1).id, 10);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(10), 2).id, 11);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(11), 0).id, 12);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(11), 1).id, 13);
-        assert_eq!(wc.get_virtual_player(&wc.get_player(11), 2).id, 14);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(3), 0).unwrap().id, 0);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(3), 1).unwrap().id, 1);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(4), 0).unwrap().id, 2);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(4), 1).unwrap().id, 3);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(5), 0).unwrap().id, 4);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(5), 1).unwrap().id, 5);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(9), 0).unwrap().id, 6);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(9), 1).unwrap().id, 7);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(9), 2).unwrap().id, 8);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(10), 0).unwrap().id, 9);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(10), 1).unwrap().id, 10);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(10), 2).unwrap().id, 11);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(11), 0).unwrap().id, 12);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(11), 1).unwrap().id, 13);
+        assert_eq!(wc.get_virtual_player(&wc.get_player(11), 2).unwrap().id, 14);
+    }
+
+    #[test]
+    fn test_get_virtual_player_j_out_of_bounds() {
+        // weight of player 0 is 2, so j=2 should return Err
+        let wc = WeightedConfigBlstrs::new(1, vec![2, 3]).unwrap();
+        let player0 = wc.get_player(0);
+        assert!(wc.get_virtual_player(&player0, 0).is_ok());
+        assert!(wc.get_virtual_player(&player0, 1).is_ok());
+        let err = wc.get_virtual_player(&player0, 2).unwrap_err();
+        let msg = format!("{err}");
+        assert!(
+            msg.contains("out of bounds"),
+            "unexpected error message: {msg}"
+        );
+    }
+
+    #[test]
+    fn test_get_virtual_player_player_id_out_of_bounds() {
+        let wc = WeightedConfigBlstrs::new(1, vec![2, 3]).unwrap();
+        let bogus_player = Player { id: 99 };
+        let err = wc.get_virtual_player(&bogus_player, 0).unwrap_err();
+        let msg = format!("{err}");
+        assert!(
+            msg.contains("out of bounds"),
+            "unexpected error message: {msg}"
+        );
     }
 }
```

### crates/aptos-dkg/src/pvss/chunky/hkzg_chunked_elgamal.rs
```diff
@@ -204,7 +204,9 @@ impl<'a, E: Pairing> Proof<'a, E> {
                 chunked_elgamal::CodomainShape {
                     chunks: (0..sc.get_total_num_players())
                         .map(|i| {
-                            let w = sc.get_player_weight(&sc.get_player(i)); // TODO: combine these functions...
+                            let w = sc
+                                .get_player_weight(&sc.get_player(i))
+                                .expect("player id from sc.get_player is in bounds"); // TODO: combine these functions...
                             (0..w)
                                 .map(|_| unsafe_random_points(number_of_chunks_per_share, rng))
                                 .collect()
@@ -221,7 +223,9 @@ impl<'a, E: Pairing> Proof<'a, E> {
                     univariate_hiding_kzg::CommitmentRandomness::<E::ScalarField>::rand(rng),
                 chunked_plaintexts: (0..sc.get_total_num_players())
                     .map(|i| {
-                        let w = sc.get_player_weight(&sc.get_player(i)); // TODO: combine these functions...
+                        let w = sc
+                            .get_player_weight(&sc.get_player(i))
+                            .expect("player id from sc.get_player is in bounds"); // TODO: combine these functions...
                         (0..w)
                             .map(|_| {
                                 Scalar::vec_from_inner(sample_field_elements(
```

### crates/aptos-dkg/src/pvss/chunky/subtranscript.rs
```diff
@@ -108,7 +108,11 @@ impl<const N: usize, P: FpConfig<N>, E: Pairing<ScalarField = Fp<P, N>>> Transcr
         pp: &Self::PublicParameters,
     ) -> (Self::DealtSecretKeyShare, Self::DealtPubKeyShare) {
         let Cs = &self.Cs[player.id];
-        debug_assert_eq!(Cs.len(), sc.get_player_weight(player));
+        debug_assert_eq!(
+            Cs.len(),
+            sc.get_player_weight(player)
+                .expect("player id is in bounds")
+        );
 
         if !Cs.is_empty()
             && let Some(first_key) = self.Rs.first()
@@ -301,7 +305,9 @@ impl<E: Pairing> Subtranscript<E> {
         let Cs: Vec<Vec<Vec<E::G1Affine>>> = (0..sc.get_total_num_players())
             .map(|i| {
                 let player = sc.get_player(i);
-                let w = sc.get_player_weight(&player);
+                let w = sc
+                    .get_player_weight(&player)
+                    .expect("player id from sc.get_player is in bounds");
                 repeat_with(|| unsafe_random_points(num_chunks_per_share, rng))
                     .take(w)
                     .collect()
```

### crates/aptos-dkg/src/pvss/chunky/verify_common.rs
```diff
@@ -103,7 +103,7 @@ pub fn verify_weighted_preamble<'a, A: Serialize + Clone, E: Pairing>(
 
     for i in 0..sc.get_total_num_players() {
         let player = sc.get_player(i);
-        let expected_weight = sc.get_player_weight(&player);
+        let expected_weight = sc.get_player_weight(&player)?;
         let got_cs = subtrs.Cs[i].len();
         if got_cs != expected_weight {
             bail!(
```

### crates/aptos-dkg/src/pvss/das/weighted_protocol.rs
```diff
@@ -104,7 +104,9 @@ impl traits::TranscriptCore for Transcript {
         sc: &Self::SecretSharingConfig,
         player: &Player,
     ) -> Self::DealtPubKeyShare {
-        let weight = sc.get_player_weight(player);
+        let weight = sc
+            .get_player_weight(player)
+            .expect("player id is in bounds");
         let mut pk_shares = Vec::with_capacity(weight);
 
         for j in 0..weight {
@@ -129,7 +131,9 @@ impl traits::TranscriptCore for Transcript {
         dk: &Self::DecryptPrivKey,
         _pp: &Self::PublicParameters,
     ) -> (Self::DealtSecretKeyShare, Self::DealtPubKeyShare) {
-        let weight = sc.get_player_weight(player);
+        let weight = sc
+            .get_player_weight(player)
+            .expect("player id is in bounds");
         let mut sk_shares = Vec::with_capacity(weight);
         let pk_shares = self.get_public_key_share(sc, player);
 
@@ -208,7 +212,9 @@ impl traits::Transcript for Transcript {
 
         let mut C = Vec::with_capacity(W);
         for i in 0..n {
-            let w_i = sc.get_player_weight(&sc.get_player(i));
+            let w_i = sc
+                .get_player_weight(&sc.get_player(i))
+                .expect("player id from sc.get_player is in bounds");
 
             let bases = vec![h, Into::<G1Projective>::into(&eks[i])];
             for j in 0..w_i {
@@ -344,7 +350,7 @@ impl AggregatableTranscript for Transcript {
 
         for i in 0..n {
             let p = sc.get_player(i);
-            let weight = sc.get_player_weight(&p);
+            let weight = sc.get_player_weight(&p)?;
             let s_i = sc.get_player_starting_index(&p);
 
             lc_R_hat.push(g2_multi_exp(
@@ -518,7 +524,7 @@ impl Transcript {
             .collect::<Vec<G1Affine>>();
         for i in 0..n {
             let p = sc.get_player(i);
-            let weight = sc.get_player_weight(&p);
+            let weight = sc.get_player_weight(&p)?;
             for j in 0..weight {
                 let k = sc.get_share_index(i, j).unwrap();
                 let lhs = pairing(&h_1_aff, &V_hat_aff[k]).add(pairing(&eks[i], &R_hat_aff[k]));
```

### crates/aptos-dkg/src/pvss/weighted/generic_weighting.rs
```diff
@@ -55,7 +55,9 @@ impl<T: Transcript> GenericWeighting<T> {
 
         for (player_id, ek) in eks.iter().enumerate() {
             let player = sc.get_player(player_id);
-            let num_shares = sc.get_player_weight(&player);
+            let num_shares = sc
+                .get_player_weight(&player)
+                .expect("player id from sc.get_player is in bounds");
             for _ in 0..num_shares {
                 duplicated_eks.push(ek.clone());
             }
@@ -84,12 +86,16 @@ impl<T: Transcript + TranscriptCore<SecretSharingConfig = ThresholdConfigBlstrs>
         sc: &Self::SecretSharingConfig,
         player: &Player,
     ) -> Self::DealtPubKeyShare {
-        let weight = sc.get_player_weight(player);
+        let weight = sc
+            .get_player_weight(player)
+            .expect("player id is in bounds");
 
         let mut dpk_share = Vec::with_capacity(weight);
 
         for i in 0..weight {
-            let virtual_player = sc.get_virtual_player(player, i);
+            let virtual_player = sc
+                .get_virtual_player(player, i)
+                .expect("i < weight holds by construction");
             dpk_share.push(T::get_public_key_share(
                 &self.trx,
                 sc.get_threshold_config(),
@@ -111,13 +117,17 @@ impl<T: Transcript + TranscriptCore<SecretSharingConfig = ThresholdConfigBlstrs>
         dk: &Self::DecryptPrivKey,
         pp: &Self::PublicParameters,
     ) -> (Self::DealtSecretKeyShare, Self::DealtPubKeyShare) {
-        let weight = sc.get_player_weight(player);
+        let weight = sc
+            .get_player_weight(player)
+            .expect("player id is in bounds");
 
         let mut weighted_dsk_share = Vec::with_capacity(weight);
         let mut weighted_dpk_share = Vec::with_capacity(weight);
 
         for i in 0..weight {
-            let virtual_player = sc.get_virtual_player(player, i);
+            let virtual_player = sc
+                .get_virtual_player(player, i)
+                .expect("i < weight holds by construction");
             let (dsk_share, dpk_share) = T::decrypt_own_share(
                 &self.trx,
                 sc.get_threshold_config(),
```

### crates/aptos-dkg/src/weighted_vuf/bls/mod.rs
```diff
@@ -113,8 +113,15 @@ impl WeightedVUF for BlsWUF {
         let mut sub_player_ids = Vec::with_capacity(wc.get_total_weight());
 
         for (player, _, _) in apks_and_proofs {
-            for j in 0..wc.get_player_weight(player) {
-                sub_player_ids.push(wc.get_virtual_player(player, j).id);
+            let weight = wc
+                .get_player_weight(player)
+                .expect("player id is in bounds");
+            for j in 0..weight {
+                sub_player_ids.push(
+                    wc.get_virtual_player(player, j)
+                        .expect("j < weight holds by construction")
+                        .id,
+                );
             }
         }
 
```

### crates/aptos-dkg/src/weighted_vuf/pinkas/mod.rs
```diff
@@ -296,8 +296,13 @@ impl PinkasWUF {
 
         let mut k = 0;
         for (player, share) in proof {
-            for j in 0..wc.get_player_weight(player) {
-                sub_player_ids.push(wc.get_virtual_player(player, j).id);
+            let w = wc.get_player_weight(player)?;
+            for j in 0..w {
+                sub_player_ids.push(
+                    wc.get_virtual_player(player, j)
+                        .expect("j < weight holds by construction")
+                        .id,
+                );
             }
 
             let apk = apks[player.id]
@@ -307,7 +312,6 @@ impl PinkasWUF {
             rks.push(&apk.0.rks);
             shares.push(share);
 
-            let w = wc.get_player_weight(player);
             ranges.push(k..k + w);
             k += w;
         }
```
