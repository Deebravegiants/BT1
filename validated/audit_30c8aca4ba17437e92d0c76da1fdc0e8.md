No vulnerability found for this question.

**Analysis:** The premise of this finding requires a "deliberately inconsistent `get_player_weight`/`get_virtual_player` pair," but no such inconsistency can arise in the actual production code. Both methods are implemented on the same `WeightedConfig<TC>` struct and derive their values from the identical `self.weights` field: `get_player_weight` does `self.weights.get(player.id)` and `get_virtual_player` independently does `self.weights.get(player.id)` for its own bounds check [1](#0-0) . There is no code path, attacker-controlled or otherwise, that lets these two accessors diverge for a real `WeightedConfigBlstrs` instance — they are structurally guaranteed to agree by construction, and `WeightedConfig::new` itself computes `weights`, `starting_index`, `max_weight`, and `min_weight` together from a single caller-supplied vector at config-creation time [2](#0-1) .

The loop bound `i` in `get_public_key_share` and `decrypt_own_share` in `generic_weighting.rs` is not attacker-controlled — it is the range `0..weight` computed from `sc.get_player_weight(player)` within the same trusted config object, and `get_virtual_player` re-validates `j < weight` against that same `weights` vector before returning `Ok` [3](#0-2) [4](#0-3) . Both `get_virtual_player` and `get_player_weight` return `anyhow::Result`, and any out-of-bounds `player.id` is already rejected with an explicit error rather than silently mismatching lengths, as confirmed by the existing unit tests `test_get_virtual_player_j_out_of_bounds` and `test_get_virtual_player_player_id_out_of_bounds` [5](#0-4) .

Additionally, this fails the review bounds: `WeightedConfig` instances used in Aptos DKG are constructed from validator-set/on-chain-stake-derived weights, not from arbitrary unprivileged transaction/API input, and this code is a low-level cryptographic library primitive, not itself a custody boundary that gates resource-account signer eligibility, ownership, or asset transfer. No unprivileged entrypoint reaches a state where these two functions can actually disagree.

### Citations

**File:** crates/aptos-crypto/src/weighted_config.rs (L66-104)
```rust
    pub fn new(threshold_weight: usize, weights: Vec<usize>) -> anyhow::Result<Self> {
        if threshold_weight == 0 {
            return Err(anyhow!(
                "expected the minimum reconstruction weight to be > 0"
            ));
        }

        if weights.is_empty() {
            return Err(anyhow!("expected a non-empty vector of player weights"));
        }
        let max_weight = *weights.iter().max().unwrap();
        let min_weight = *weights.iter().min().unwrap();

        let n = weights.len();
        let W = weights.iter().sum();

        // e.g., Suppose the weights for players 0, 1 and 2 are [2, 4, 3]
        // Then, our PVSS transcript implementation will store a vector of 2 + 4 + 3 = 9 shares,
        // such that:
        //  - Player 0 will own the shares at indices [0..2), i.e.,starting index 0
        //  - Player 1 will own the shares at indices [2..2 + 4) = [2..6), i.e.,starting index 2
        //  - Player 2 will own the shares at indices [6, 6 + 3) = [6..9), i.e., starting index 6
        let mut starting_index = Vec::with_capacity(weights.len());
        starting_index.push(0);

        for w in weights.iter().take(n - 1) {
            starting_index.push(starting_index.last().unwrap() + w);
        }

        let tc = TC::new(threshold_weight, W)?;
        Ok(WeightedConfig {
            tc,
            num_players: n,
            weights,
            starting_index,
            max_weight,
            min_weight,
        })
    }
```

**File:** crates/aptos-crypto/src/weighted_config.rs (L164-207)
```rust
    pub fn get_player_weight(&self, player: &Player) -> anyhow::Result<usize> {
        self.weights.get(player.id).copied().ok_or_else(|| {
            anyhow!(
                "get_player_weight: player id {} out of bounds (num_players={})",
                player.id,
                self.num_players
            )
        })
    }

    /// Returns the starting index of a player's shares in the flattened vector of all weighted shares.
    pub fn get_player_starting_index(&self, player: &Player) -> usize {
        self.starting_index[player.id]
    }

    /// In an unweighted secret sharing scheme, each player has one share. We can weigh such a scheme
    /// by splitting a player into as many "virtual" players as that player's weight, assigning one
    /// share per "virtual player."
    ///
    /// This function returns the "virtual" player associated with the $i$th sub-share of this player.
    ///
    /// Returns an error if `player.id` is out of bounds or if `j` is greater than
    /// or equal to `player`'s weight. This makes the function safe to call with
    /// untrusted input (e.g. attacker-controlled `Player` ids or share vector
    /// lengths) without panicking the process.
    pub fn get_virtual_player(&self, player: &Player, j: usize) -> anyhow::Result<Player> {
        let weight = self.weights.get(player.id).copied().ok_or_else(|| {
            anyhow!(
                "get_virtual_player: player id {} out of bounds (num_players={})",
                player.id,
                self.num_players
            )
        })?;
        ensure!(
            j < weight,
            "get_virtual_player: share index {} out of bounds for player {} (weight={})",
            j,
            player.id,
            weight
        );
        Ok(Player {
            id: self.starting_index[player.id] + j,
        })
    }
```

**File:** crates/aptos-crypto/src/weighted_config.rs (L542-567)
```rust
    #[test]
    fn test_get_virtual_player_j_out_of_bounds() {
        // weight of player 0 is 2, so j=2 should return Err
        let wc = WeightedConfigBlstrs::new(1, vec![2, 3]).unwrap();
        let player0 = wc.get_player(0);
        assert!(wc.get_virtual_player(&player0, 0).is_ok());
        assert!(wc.get_virtual_player(&player0, 1).is_ok());
        let err = wc.get_virtual_player(&player0, 2).unwrap_err();
        let msg = format!("{err}");
        assert!(
            msg.contains("out of bounds"),
            "unexpected error message: {msg}"
        );
    }

    #[test]
    fn test_get_virtual_player_player_id_out_of_bounds() {
        let wc = WeightedConfigBlstrs::new(1, vec![2, 3]).unwrap();
        let bogus_player = Player { id: 99 };
        let err = wc.get_virtual_player(&bogus_player, 0).unwrap_err();
        let msg = format!("{err}");
        assert!(
            msg.contains("out of bounds"),
            "unexpected error message: {msg}"
        );
    }
```

**File:** crates/aptos-dkg/src/pvss/weighted/generic_weighting.rs (L89-107)
```rust
        let weight = sc
            .get_player_weight(player)
            .expect("player id is in bounds");

        let mut dpk_share = Vec::with_capacity(weight);

        for i in 0..weight {
            let virtual_player = sc
                .get_virtual_player(player, i)
                .expect("i < weight holds by construction");
            dpk_share.push(T::get_public_key_share(
                &self.trx,
                sc.get_threshold_config(),
                &virtual_player,
            ));
        }

        dpk_share
    }
```

**File:** crates/aptos-dkg/src/pvss/weighted/generic_weighting.rs (L120-143)
```rust
        let weight = sc
            .get_player_weight(player)
            .expect("player id is in bounds");

        let mut weighted_dsk_share = Vec::with_capacity(weight);
        let mut weighted_dpk_share = Vec::with_capacity(weight);

        for i in 0..weight {
            let virtual_player = sc
                .get_virtual_player(player, i)
                .expect("i < weight holds by construction");
            let (dsk_share, dpk_share) = T::decrypt_own_share(
                &self.trx,
                sc.get_threshold_config(),
                &virtual_player,
                dk,
                pp,
            );
            weighted_dsk_share.push(dsk_share);
            weighted_dpk_share.push(dpk_share);
        }

        (weighted_dsk_share, weighted_dpk_share)
    }
```
