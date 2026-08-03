No vulnerability found for this question.

**Analysis:**

The `flattened_shares.truncate(sc.get_threshold_weight())` call in the `Reconstructable<WeightedConfigArkworks<F>>` impl [1](#0-0)  is part of the DKG/PVSS secret-reconstruction machinery used for consensus randomness (`ChunkyDKGSession`, `real_dkg`, `randomness_dkg`) [2](#0-1) , not for code-object upgrade authorization. There is no code path connecting this reconstruction routine to Move object/package upgrade authority checks.

More importantly, the premise misunderstands Shamir-style threshold secret sharing: reconstruction is designed to produce the *same unique secret* from **any** eligible subset of valid shares whose combined weight meets the threshold, regardless of *which* specific players' shares are used or their ordering. The shares fed into `reconstruct` are not arbitrary attacker-supplied values — they originate from PVSS transcripts that are cryptographically verified against public commitments before reconstruction is attempted (see `trx.verify(...)` in the DKG test harness [3](#0-2) , mirrored in production DKG session logic). An attacker cannot substitute a "low-weight attacker-supplied" share with an arbitrary value and have it pass verification unless it is a genuine, correctly-computed share consistent with the dealt polynomial. Truncating the flattened list to `threshold_weight` shares — regardless of which players they belong to — still yields the correct secret as long as all included shares are valid, which is the entire point of the threshold scheme; there is no invariant that "only high-weight players" must determine the secret.

Additionally, this logic executes entirely within validator/consensus-internal DKG code, not on an unprivileged transaction, package, view, authenticator, API, bytecode, or proof-input surface as required by the review bounds. No custody boundary (object ownership, FA supply/holder identity, multisig/resource-account/code-object authority) is touched by this code at all. [4](#0-3)

### Citations

**File:** crates/aptos-crypto/src/weighted_config.rs (L404-444)
```rust
/// Implements weighted reconstruction of a secret `SK` through the existing unweighted reconstruction
/// implementation of `SK`.
impl<SK: Reconstructable<ThresholdConfigBlstrs>> Reconstructable<WeightedConfigBlstrs> for SK {
    type ShareValue = Vec<SK::ShareValue>;

    fn reconstruct(
        sc: &WeightedConfigBlstrs,
        shares: &[ShamirShare<Self::ShareValue>],
    ) -> anyhow::Result<Self> {
        let mut flattened_shares = Vec::with_capacity(sc.get_total_weight());

        // println!();
        for (player, sub_shares) in shares {
            // println!(
            //     "Flattening {} share(s) for player {player}",
            //     sub_shares.len()
            // );
            let expected_weight = sc.get_player_weight(player)?;
            ensure!(
                sub_shares.len() == expected_weight,
                "reconstruct: player {} has {} sub-shares but expected weight {}",
                player.id,
                sub_shares.len(),
                expected_weight
            );
            for (pos, share) in sub_shares.iter().enumerate() {
                let virtual_player = sc.get_virtual_player(player, pos)?;

                // println!(
                //     " + Adding share {pos} as virtual player {virtual_player}: {:?}",
                //     share
                // );
                // TODO(Performance): Avoiding the cloning here might be nice
                let tuple = (virtual_player, share.clone());
                flattened_shares.push(tuple);
            }
        }

        SK::reconstruct(sc.get_threshold_config(), &flattened_shares)
    }
}
```

**File:** crates/aptos-crypto/src/weighted_config.rs (L453-488)
```rust
    fn reconstruct(
        sc: &WeightedConfigArkworks<F>,
        shares: &[ShamirShare<Self::ShareValue>],
    ) -> anyhow::Result<Self> {
        let mut flattened_shares = Vec::with_capacity(sc.get_total_weight());

        // println!();
        for (player, sub_shares) in shares {
            // println!(
            //     "Flattening {} share(s) for player {player}",
            //     sub_shares.len()
            // );
            let expected_weight = sc.get_player_weight(player)?;
            ensure!(
                sub_shares.len() == expected_weight,
                "reconstruct: player {} has {} sub-shares but expected weight {}",
                player.id,
                sub_shares.len(),
                expected_weight
            );
            for (pos, share) in sub_shares.iter().enumerate() {
                let virtual_player = sc.get_virtual_player(player, pos)?;

                // println!(
                //     " + Adding share {pos} as virtual player {virtual_player}: {:?}",
                //     share
                // );
                // TODO(Performance): Avoiding the cloning here might be nice
                let tuple = (virtual_player, share.clone());
                flattened_shares.push(tuple);
            }
        }
        flattened_shares.truncate(sc.get_threshold_weight());

        SK::reconstruct(sc.get_threshold_config(), &flattened_shares)
    }
```

**File:** types/src/dkg/chunky_dkg.rs (L345-405)
```rust
impl ChunkyDKGSession {
    /// Create a new DKG session from on-chain session metadata.
    pub fn new(dkg_session_metadata: &ChunkyDKGSessionMetadata) -> Arc<ChunkyDKGSession> {
        let onchain_config = dkg_session_metadata
            .into_on_chain_chunky_dkg_config()
            .unwrap_or_else(OnChainChunkyDKGConfig::default_disabled);
        let secrecy_threshold = onchain_config
            .secrecy_threshold()
            .unwrap_or_else(|| *DEFAULT_SECRECY_THRESHOLD);
        let reconstruct_threshold = onchain_config
            .reconstruct_threshold()
            .unwrap_or_else(|| *DEFAULT_RECONSTRUCT_THRESHOLD);
        let reconstruct_threshold = max(reconstruct_threshold, secrecy_threshold + U64F64::DELTA);

        let target_validators = dkg_session_metadata.target_validator_consensus_infos_cloned();
        let validator_stakes: Vec<u64> =
            target_validators.iter().map(|vi| vi.voting_power).collect();

        let eks: Vec<ChunkyEncryptPubKey> = target_validators
            .iter()
            .map(|vi| (&vi.public_key).into())
            .collect();

        let profile = DKGRoundingProfile::new(
            &validator_stakes,
            secrecy_threshold,
            reconstruct_threshold,
            None,
        )
        .unwrap_or_else(|_| {
            DKGRoundingProfile::infallible(
                &validator_stakes,
                secrecy_threshold,
                reconstruct_threshold,
                None,
            )
        });

        // Create WeightedConfigArkworks<Fr> from the computed weights
        let threshold_config = ChunkyDKGThresholdConfig::new(
            profile.reconstruct_threshold_in_weights as usize,
            profile
                .validator_weights
                .iter()
                .map(|w| *w as usize)
                .collect(),
        )
        .expect("Failed to create WeightedConfigArkworks");

        let public_parameters = PUBLIC_PARAMETERS
            .as_ref()
            .expect("PublicParameters not initialized; call initialize_public_parameters first")
            .clone();

        Arc::new(ChunkyDKGSession {
            threshold_config,
            public_parameters,
            session_metadata: dkg_session_metadata.clone(),
            eks,
        })
    }
```

**File:** crates/aptos-dkg/tests/dkg.rs (L69-79)
```rust
    // Verify the aggregated transcript
    trx.verify(
        sc,
        &d.pp,
        &d.spks,
        &d.eks,
        &(0..sc.get_total_num_players())
            .map(|_| NoAux)
            .collect::<Vec<NoAux>>(),
    )
    .expect("aggregated PVSS transcript failed verification");
```
