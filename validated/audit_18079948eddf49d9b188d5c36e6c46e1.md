## Confirmed local candidate: Precomputed validator-set cache goes stale between DKG start and epoch finalization

### Title
Stale `PrecomputedValidatorSet` overwrites live stake/reward state at epoch change, causing validator voting power to diverge from actual custody balances - (`aptos-move/framework/aptos-framework/sources/stake.move`)

### Summary
`stake::next_validator_consensus_infos_v2()` snapshots the next-epoch validator set (including each validator's `voting_power`, derived from stake balances) at the moment DKG starts, and stores it in `PrecomputedValidatorSet`. This snapshot is consumed later, unconditionally, by `on_new_epoch()`, which overwrites the freshly-updated `ValidatorSet` (after `update_stake_pool` has already applied rewards/fees to the real `StakePool` coin balances) with the old cached numbers.

### Finding Description
`next_validator_consensus_infos_v2()` [1](#0-0)  is invoked at DKG start via `reconfiguration_with_dkg::try_start`/`try_start_with_chunky_dkg` [2](#0-1) . It computes `voting_power` per candidate from the *current* `StakePool` coin balances at that instant and can cache the result in `PrecomputedValidatorSet` for reuse.

DKG can run for an extended, variable period (it is only finalized once consensus completes DKG/chunky DKG, or a grace-period/emergency watchdog fires) [3](#0-2) . During this window, `add_stake`, `unlock`, `reactivate_stake`, and delegation-pool operations can still change a validator's real stake/coin balance [4](#0-3) .

When the epoch actually turns over, `on_new_epoch()` first calls `update_stake_pool` for every active/pending_inactive validator, which mutates the real `StakePool` resources (rewards, fees) [5](#0-4) . It then, if a `PrecomputedValidatorSet` exists, unconditionally does `*validator_set = precomputed`, replacing the entire `ValidatorSet` (including every validator's `voting_power` and `total_voting_power`) with the value computed at DKG-start time, instead of recomputing it from the just-updated `StakePool` state [6](#0-5) . The code comment explicitly frames this as a "cached value" substituted for live recomputation "to avoid the O(n) per-validator recomputation" — i.e. exactly the same class of bug as the Booster report: a derived value (voting power / "booster") is cached against a reference quantity that can change (stake balance / `athBalance`), and is not recalculated at the point of consumption.

### Impact Explanation
`ValidatorInfo.voting_power` is the on-chain source of truth for a validator's/staking-pool's economic weight — it directly gates validator-set admission (`voting_power >= minimum_stake`) and is used by `aptos_governance`/`delegation_pool` voting-power accounting that is built on `stake_pool` state. Because the stored `voting_power` in `ValidatorSet` becomes decoupled from the actual underlying `StakePool` coin balance for the entire next epoch, the recorded voting/reward-eligibility figures do not reflect real custody of stake: a validator's real stake can grow (rewards, `add_stake`) or shrink (`unlock`) after the snapshot was taken, but the effective, protocol-recognized voting power/"stake" is frozen at the older figure. This is a supply/custody-accounting corruption: the value used to gate consensus participation and (indirectly) reward/commission distribution no longer matches the actual asset holdings it's supposed to represent, for the length of one full epoch, silently, on every DKG-based reconfiguration.

### Likelihood Explanation
DKG-based reconfiguration is the default epoch-change path, and its duration is variable and can span multiple blocks/transactions (bounded only by a grace period/emergency watchdog) [7](#0-6) . Any permissionless stake operation (`add_stake`, `unlock`, `reactivate_stake`) executed by any validator/delegator during that window will trigger the staleness, so this is not a contrived edge case — it can occur on essentially every epoch transition where any stake modification happens between DKG start and DKG completion.

### Recommendation
At the point `PrecomputedValidatorSet` is consumed in `on_new_epoch`, either (a) invalidate/recompute the cache if any stake-affecting operation happened after it was captured, or (b) merge live `StakePool` balances (post `update_stake_pool`) into the cached `ValidatorInfo` entries rather than overwriting `voting_power`/`total_voting_power` wholesale from the stale snapshot, mirroring the `refresh_validator_set_in_place` recomputation path that is already used when no cache exists.

### Proof of Concept
Conceptual sequence (Move pseudo-flow, based on the cited functions):
1. Epoch N-1 nears expiration; `reconfiguration_with_dkg::try_start()` fires, calling `stake::next_validator_consensus_infos_v2()`, which computes and stores `PrecomputedValidatorSet` with validator V's `voting_power = X` based on `StakePool[V].active` at that instant.
2. Before DKG finishes (which can take multiple blocks), validator V (or a delegator) calls `stake::add_stake` or accrues rewards, increasing `StakePool[V].active` to `X + Y`.
3. DKG completes; `reconfiguration_with_dkg::finish()` → `reconfiguration::reconfigure()` → `stake::on_new_epoch()` runs. `update_stake_pool` for V correctly applies rewards to `StakePool[V]`, but then `*validator_set = precomputed` overwrites `ValidatorInfo` for V back to `voting_power = X`, discarding the additional `Y` from the recorded on-chain voting/consensus weight for the entirety of epoch N, even though V's real stake balance is `X + Y`.

I was not able to trace, within the available index, the exact production trigger that decides whether `PrecomputedValidatorSet` is invalidated on intervening stake operations (I found no invalidation logic for the resource anywhere it's referenced), so I cannot rule out an invalidation mechanism existing elsewhere in `stake.move` that wasn't surfaced by search; a full-repo review (e.g., via a Devin session) of every `add_stake`/`unlock`/`reactivate_stake` path for a `move_from<PrecomputedValidatorSet>` call would be needed to fully confirm no mitigation exists.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/stake.move (L876-927)
```text
    /// Add `amount` of coins from the `account` owning the StakePool.
    public entry fun add_stake(
        owner: &signer, amount: u64
    ) acquires OwnerCapability, StakePool, ValidatorSet {
        let owner_address = signer::address_of(owner);
        assert_owner_cap_exists(owner_address);
        let ownership_cap = borrow_global<OwnerCapability>(owner_address);
        add_stake_with_cap(ownership_cap, coin::withdraw<AptosCoin>(owner, amount));
    }

    /// Add `coins` into `pool_address`. this requires the corresponding `owner_cap` to be passed in.
    public fun add_stake_with_cap(
        owner_cap: &OwnerCapability, coins: Coin<AptosCoin>
    ) acquires StakePool, ValidatorSet {
        assert_reconfig_not_in_progress();
        let pool_address = owner_cap.pool_address;
        assert_stake_pool_exists(pool_address);

        let amount = coin::value(&coins);
        if (amount == 0) {
            coin::destroy_zero(coins);
            return
        };

        // Only track and validate voting power increase for active and pending_active validator.
        // Pending_inactive validator will be removed from the validator set in the next epoch.
        // Inactive validator's total stake will be tracked when they join the validator set.
        let validator_set = borrow_global<ValidatorSet>(@aptos_framework);
        // Search directly rather using get_validator_state to save on unnecessary loops.
        if (find_validator(&validator_set.active_validators, pool_address).is_some()
            || find_validator(&validator_set.pending_active, pool_address).is_some()) {
            update_voting_power_increase(amount);
        };

        // Add to pending_active if it's a current validator because the stake is not counted until the next epoch.
        // Otherwise, the delegation can be added to active directly as the validator is also activated in the epoch.
        let stake_pool = borrow_global_mut<StakePool>(pool_address);
        if (is_current_epoch_validator(pool_address)) {
            coin::merge<AptosCoin>(&mut stake_pool.pending_active, coins);
        } else {
            coin::merge<AptosCoin>(&mut stake_pool.active, coins);
        };

        let (_, maximum_stake) =
            staking_config::get_required_stake(&staking_config::get());
        let voting_power = get_voting_power(stake_pool);
        assert!(
            voting_power <= maximum_stake, error::invalid_argument(ESTAKE_EXCEEDS_MAX)
        );

        event::emit(AddStake { pool_address, amount_added: amount });
    }
```

**File:** aptos-move/framework/aptos-framework/sources/stake.move (L1348-1359)
```text
        // Process pending stake and distribute transaction fees and rewards for each currently active validator.
        validator_set.active_validators.for_each_ref(|validator| {
            let validator: &ValidatorInfo = validator;
            update_stake_pool(validator_perf, validator.addr, &config);
        });

        // Process pending stake and distribute transaction fees and rewards for each currently pending_inactive validator
        // (requested to leave but not removed yet).
        validator_set.pending_inactive.for_each_ref(|validator| {
            let validator: &ValidatorInfo = validator;
            update_stake_pool(validator_perf, validator.addr, &config);
        });
```

**File:** aptos-move/framework/aptos-framework/sources/stake.move (L1384-1404)
```text
        // Determine the next-epoch active set: either consume the cached value
        // produced when reconfig started (async/DKG path), or compute it now from
        // live state (sync/governance path). The two paths are mutually exclusive,
        // so we avoid the O(n) per-validator recomputation when the cache exists.
        let liveness_fallback_event = if (exists<PrecomputedValidatorSet>(@aptos_framework)) {
            let PrecomputedValidatorSet { validator_set: precomputed, is_liveness_fallback } =
                move_from<PrecomputedValidatorSet>(@aptos_framework);
            *validator_set = precomputed;
            if (is_liveness_fallback) {
                let (minimum_stake, _) = staking_config::get_required_stake(&config);
                option::some(ValidatorSetLivenessFallback {
                    minimum_stake,
                    emergency_validator_count: validator_set.active_validators.length(),
                    total_emergency_voting_power: validator_set.total_voting_power,
                })
            } else {
                option::none()
            }
        } else {
            refresh_validator_set_in_place(validator_set, &config)
        };
```

**File:** aptos-move/framework/aptos-framework/sources/stake.move (L1636-1649)
```text
    /// Pre-compute the next validator set and store the result.
    /// Should only be called when reconfiguration starts.
    public(friend) fun next_validator_consensus_infos_v2(): ValidatorSet acquires PrecomputedValidatorSet, ValidatorSet, ValidatorPerformance, StakePool, ValidatorConfig {
        if (exists<PrecomputedValidatorSet>(@aptos_framework)) {
            // Cache hit: already computed for this reconfig, return stored result.
            return borrow_global<PrecomputedValidatorSet>(@aptos_framework).validator_set;
        };

        let cur_validator_set = borrow_global<ValidatorSet>(@aptos_framework);
        let staking_config = staking_config::get();
        let validator_perf = borrow_global<ValidatorPerformance>(@aptos_framework);
        let (minimum_stake, _) = staking_config::get_required_stake(&staking_config);
        let (rewards_rate, rewards_rate_denominator) =
            staking_config::get_reward_rate(&staking_config);
```

**File:** aptos-move/framework/aptos-framework/sources/reconfiguration_with_dkg.move (L58-65)
```text
        reconfiguration_state::on_reconfig_start();
        let cur_epoch = reconfiguration::current_epoch();
        dkg::start(
            cur_epoch,
            randomness_config::current(),
            stake::cur_validator_consensus_infos(),
            validator_consensus_infos_from_validator_set(&stake::next_validator_consensus_infos_v2())
        );
```

**File:** aptos-move/framework/aptos-framework/sources/reconfiguration_with_dkg.move (L118-171)
```text
    /// Single decision point for completing the in-progress reconfig.
    /// Calls finish(account) iff:
    /// - reconfiguration is in progress, AND
    /// - DKG has no in-progress session, AND
    /// - Chunky DKG has no in-progress session, OR the configured grace period
    ///   (shadow mode) has elapsed since the chunky session started.
    /// No-op otherwise. Callers (finish_with_dkg_result,
    /// finish_with_chunky_dkg_result, try_complete_after_grace_period) just
    /// signal "something may have changed" and let this function decide.
    fun try_finalize_reconfig(account: &signer) {
        if (!reconfiguration_state::is_in_progress()) { return };

        // Emergency watchdog: force-finalize regardless of DKG state once the
        // grace period has elapsed since reconfiguration started. Equivalent
        // to `now >= last_reconfiguration_time + epoch_interval + grace_period`,
        // since `reconfiguration_state::start_time_secs()` is set when the
        // block prologue triggers reconfig after `epoch_interval` has elapsed.
        let force_end_grace = epoch_timeout_config::force_end_grace_period_secs();
        if (force_end_grace.is_some()) {
            let now_us = timestamp::now_microseconds();
            let deadline_us = reconfiguration_state::start_time_secs() * 1_000_000
                + (*force_end_grace.borrow()) * 1_000_000;
            if (now_us >= deadline_us) {
                let dkg_incomplete = dkg::incomplete_session().is_some();
                let chunky_incomplete = chunky_dkg::incomplete_session().is_some();
                event::emit(ForceEndEpochEvent::V1 {
                    epoch: reconfiguration::current_epoch(),
                    dkg_incomplete,
                    chunky_incomplete,
                    deadline_us,
                    now_us,
                });
                finish(account);
                return
            };
        };

        // DKG must be done.
        if (dkg::incomplete_session().is_some()) { return };

        // Chunky DKG must be done OR its grace period (shadow mode) must have elapsed.
        let chunky_session = chunky_dkg::incomplete_session();
        if (chunky_session.is_some()) {
            let grace_period = chunky_dkg_config::grace_period_secs();
            if (grace_period.is_none()) { return };
            let start_time_us = chunky_dkg::session_start_time(chunky_session.borrow());
            let grace_period_us = (*grace_period.borrow()) * 1_000_000;
            if (timestamp::now_microseconds() - start_time_us < grace_period_us) {
                return
            };
        };

        finish(account);
    }
```
