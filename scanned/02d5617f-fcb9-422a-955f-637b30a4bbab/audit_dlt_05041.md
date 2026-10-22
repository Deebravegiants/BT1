# [M] set_weights / commit_weights family is Pays::No with the per-neuron rate limit enforced only in the dispatch body, enabling fee-free block-fill flooding

## Summary
Severity: Medium
Chain: Bittensor
Component: opentensor/subtensor
CWE: Allocation of Resources Without Limits or Throttling
Published: 2026-06-17
Source: https://github.com/RaoFoundation/subtensor/security/advisories/GHSA-h98r-p37h-h4mv
Type: github-advisory

## Details
## Summary

The entire `set_weights` / `commit_weights` / `reveal_weights` family of extrinsics is declared `Pays::No` with an accurately-benchmarked `DispatchClass::Normal` weight. The transaction-validity `SignedExtension` (`SubtensorTransactionExtension::validate`) gates these calls **only** on `check_weights_min_stake` — a one-time minimum-stake check. The per-neuron weight-setting rate limit (`WeightsSetRateLimit`, default 100 blocks) is enforced **only inside the dispatch body** via `ensure!`, which returns an error but, because the call is `Pays::No` and returns a plain `DispatchResult` with no `actual_weight` refund, still consumes the full ~16.9 billion ps of benchmarked block weight for **zero fee**.

A single account holding one min-stake UID can therefore pack a block with many over-rate `set_weights` transactions: all pass `validate`, all are included free, the first succeeds and the rest fail rate-limiting at execution — each burning its declared Normal-class weight at no cost. The result is a fee-free block-fill / congestion primitive against the Normal dispatch class (transfers, staking, etc.). This is the same pattern the maintainers already defend against in `validate` for `register_network`, `serve_axon`, and `associate_evm_key`; the omission for weights is an inconsistency, not a deliberate design.

## Details

### 1. The weight calls are `Pays::No`, `Normal`, accurately benchmarked

`pallets/subtensor/src/macros/dispatches.rs:84-85`:

```rust
#[pallet::call_index(0)]
#[pallet::weight((<T as crate::pallet::Config>::WeightInfo::set_weights(), DispatchClass::Normal, Pays::No))]
pub fn set_weights(
```

The benchmarked weight is large and non-trivial — `pallets/subtensor/src/weights.rs:2617-2625`:

```rust
fn set_weights() -> Weight {
    // Minimum execution time: 16_598_698_000 picoseconds.
    Weight::from_parts(16_897_861_000, 10327382)
        .saturating_add(RocksDbWeight::get().reads(4112_u64))
        .saturating_add(RocksDbWeight::get().writes(2_u64))
}
```

The same `(WeightInfo::…, DispatchClass::Normal, Pays::No)` shape is repeated across the whole family: `set_mechanism_weights` (dispatches.rs:161-164), `batch_set_weights` (205-206), `commit_weights` (235-236), `commit_mechanism_weights` (267-270), `batch_commit_weights` (302-303), `reveal_weights` (349-350), `reveal_mechanism_weights` (402-405), `batch_reveal_weights` (560-561), `commit_crv3_mechanism_weights` (500-503), `commit_timelocked_weights` (2019-2020), `commit_timelocked_mechanism_weights` (2120-2123).

### 2. `validate` gates only on minimum stake, never on the rate limit

`pallets/subtensor/src/extensions/subtensor.rs:244-251` (representative of the family):

```rust
Some(Call::set_weights { netuid, .. })
| Some(Call::set_mechanism_weights { netuid, .. }) => {
    if Self::check_weights_min_stake(who, *netuid) {
        Ok((Default::default(), (), origin))
    } else {
        Err(CustomTransactionError::StakeAmountTooLow.into())
    }
}
```

Every branch for the weights family (`commit_weights`/`commit_mechanism_weights` at 114-122, `batch_commit_weights` at 123-137, `reveal_weights` at 138-166, `reveal_mechanism_weights` at 167-196, `batch_reveal_weights` at 197-243, `set_weights`/`set_mechanism_weights` at 244-251, `batch_set_weights` at 252-267, `commit_timelocked_*` / `commit_crv3_*` at 268-302) calls only `check_weights_min_stake` (plus, for reveals, a commit-existence / reveal-window check). None consult `WeightsSetRateLimit`.

`check_weights_min_stake` is a pure per-call eligibility gate, not a throttle — `pallets/subtensor/src/lib.rs:2687-2698`:

```rust
pub fn check_weights_min_stake(hotkey: &T::AccountId, netuid: NetUid) -> bool {
    if let Some(owner_uid) = Self::get_owner_uid(netuid)
        && Uids::<T>::get(netuid, hotkey) == Some(owner_uid)
    { return true; }
    let (total_stake, _, _) = Self::get_stake_weights_for_hotkey_on_subnet(hotkey, netuid);
    total_stake >= Self::get_stake_threshold()
}
```

Because it returns the same `true` for every transaction in the block regardless of how many the account has already sent, it provides no per-block throttling.

### 3. The rate limit lives only in the dispatch body, with no weight refund

`pallets/subtensor/src/subnets/weights.rs:804-813` (in `internal_set_weights`):

```rust
let neuron_uid = Self::get_uid_for_net_and_hotkey(netuid, &hotkey)?;
let current_block: u64 = Self::get_current_block_as_u64();
if !Self::get_commit_reveal_weights_enabled(netuid) {
    ensure!(
        Self::check_rate_limit(netuid_index, neuron_uid, current_block),
        Error::<T>::SettingWeightsTooFast
    );
}
```

`commit_weights` enforces the same in-body throttle — `weights.rs:93-97` (`CommittingWeightsTooFast`). The check itself, `weights.rs:1107-1127`, compares `current_block - last_set_weights >= WeightsSetRateLimit`; `last_set_weights == 0` (never set) passes:

```rust
let last_set_weights: u64 = Self::get_last_update_for_uid(netuid_index, neuron_uid);
if last_set_weights == 0 { return true; }
return current_block.saturating_sub(last_set_weights)
    >= Self::get_weights_set_rate_limit(netuid);
```

On success, the dispatch writes `set_last_update_for_uid(...)` (weights.rs:855 for set, weights.rs:138 for commit). Because storage mutations are visible to later extrinsics **within the same block**, only the first weight tx from a given UID succeeds; every subsequent one in that block sees the freshly-written `last_update == current_block` and fails `check_rate_limit` with `SettingWeightsTooFast` / `CommittingWeightsTooFast`.

Crucially, the extrinsic entry point returns a plain `DispatchResult` with no `PostDispatchInfo` — `weights.rs:922-930`:

```rust
pub fn do_set_weights(...) -> dispatch::DispatchResult {
    Self::internal_set_weights(origin, netuid, MechId::MAIN, uids, values, version_key)
}
```

With no `actual_weight` in the post-info, `frame_system::CheckWeight` performs no refund: the full benchmarked ~16.9 B-ps weight is committed to the block for the failed tx. Default rate limit is 100 blocks — `pallets/subtensor/src/lib.rs:750-752` returns `100`.

### 4. The transaction-validity pipeline confirms inclusion of failing txs

The runtime extension tuple (`runtime/src/lib.rs:1662-1682`) is `(CheckNonZeroSender, CheckSpecVersion, CheckTxVersion, CheckGenesis, CheckMortality, CheckNonce, CheckWeight, ChargeTransactionPaymentWrapper, …, SubtensorTransactionExtension, …)`. `CheckNonce` (line 1668) lets a single account chain many consecutive-nonce txs into one block; `CheckWeight` (line 1669) reserves and commits Normal-class weight. Since `SubtensorTransactionExtension::validate` returns `Ok` for every over-rate weight tx, all of them pass pre-dispatch, are included in the block, dispatch, and — for all but the first — fail business logic while still consuming weight at no fee (`Pays::No`).

`pallet_shield::CheckShieldedTxValidity` (the only other custom call-aware extension, `pallets/shield/src/extension.rs:51-78`) gates only `submit_encrypted` and passes all weight calls through, so it does not mitigate this.

### 5. The maintainers already replicate rate limits in `validate` elsewhere — the omission is inconsistent

`pallets/subtensor/src/extensions/subtensor.rs:381-394`:

```rust
Some(Call::register_network { .. }) => {
    if !TransactionType::RegisterNetwork.passes_rate_limit::<T>(who) {
        return Err(CustomTransactionError::RateLimitExceeded.into());
    }
    Ok((Default::default(), (), origin))
}
Some(Call::associate_evm_key { netuid, .. }) => {
    let uid = Pallet::<T>::get_uid_for_net_and_hotkey(*netuid, who)
        .map_err(|_| CustomTransactionError::UidNotFound)?;
    Pallet::<T>::ensure_evm_key_associate_rate_limit(*netuid, uid)
        .map_err(|_| CustomTransactionError::EvmKeyAssociateRateLimitExceeded)?;
    Ok((Default::default(), (), origin))
}
```

`serve_axon` / `serve_axon_tls` likewise validate the serving rate limit in `validate` via `validate_serve_axon` (subtensor.rs:315-366). The weights family is the only `Pays::No` rate-limited group whose throttle is **not** mirrored into the validity check.

## Proof of Concept / Attack Scenario

Preconditions:
- Attacker controls one hotkey registered as a UID on a target subnet whose hotkey-on-subnet stake (`get_stake_weights_for_hotkey_on_subnet`, includes delegated/nominated stake) meets `StakeThreshold`, or is the subnet owner hotkey. This is a one-time economic barrier, not a per-transaction cost.
- Commit-reveal disabled → use `set_weights`; commit-reveal enabled → use `commit_weights` (same in-dispatch-only throttle).

Steps:
1. Attacker signs N transactions of `set_weights(netuid, dests, weights, version_key)` from the same hotkey with consecutive nonces (e.g. N = 150–200 to saturate the Normal class).
2. All N pass `SubtensorTransactionExtension::validate` (only `check_weights_min_stake` is consulted, which returns `true` for every one).
3. `CheckNonce` chains them; `CheckWeight` admits them until the Normal-class budget is exhausted. Block author includes them.
4. At execution, tx #1 succeeds and writes `last_update = current_block`. Tx #2..#N all fail `check_rate_limit` (`SettingWeightsTooFast`), but each still consumes its full benchmarked ~16.9 B-ps weight, and all are `Pays::No` → **zero fees charged** for the entire batch.
5. The Normal class fills with attacker spam; legitimate Normal-class extrinsics (balance transfers, staking, take changes) are crowded out of that block. Repeat every block.

Quantification: Normal-class budget = 75% of `MAXIMUM_BLOCK_WEIGHT` = `0.75 × 4 × WEIGHT_REF_TIME_PER_SECOND` ≈ `3.0 × 10^12` ps (`runtime/src/lib.rs:287-308`). At ~`1.69 × 10^10` ps per `set_weights`, roughly **~177 transactions** fill the Normal class per block, all for free. The attacker gains: free, sustained block-fill across consecutive blocks. The victim (the network and its users) loses: Normal-class throughput / timely inclusion of competing transactions.

## Impact

- **Affected parties:** all users relying on timely inclusion of Normal-class extrinsics on the affected chain; subnet operations broadly.
- **Worst case:** sustained, fee-free congestion of the Normal dispatch class. Because the spam costs the attacker nothing per transaction (only the up-front stake to clear `StakeThreshold`, which remains the attacker's and keeps earning), the flood can be maintained indefinitely at no marginal cost, degrading transaction throughput and inflating inclusion latency for honest users.
- **Mitigating factors (why this is Medium, not High):**
  - Block production is **not** halted: inherents and the Mandatory/Operational classes are budgeted separately, so consensus liveness and governance/sudo paths are unaffected.
  - There is a real economic precondition — the attacker must hold min-subnet-stake (or own the subnet). This bounds who can mount it and gives the attacker skin in the game (though the stake is not slashed or consumed).
  - The impact is throughput degradation of one dispatch class, not loss of funds, state corruption, or integrity violation.
  - Governance can raise `StakeThreshold` or `WeightsSetRateLimit`, but neither closes the gap inside `validate`; the spam remains free until the validity gate is fixed.

## Affected Code

- `pallets/subtensor/src/macros/dispatches.rs:84-85` — `set_weights` `Pays::No`, `Normal`.
- `pallets/subtensor/src/macros/dispatches.rs:161-164` — `set_mechanism_weights` `Pays::No`.
- `pallets/subtensor/src/macros/dispatches.rs:205-206` — `batch_set_weights` `Pays::No`.
- `pallets/subtensor/src/macros/dispatches.rs:235-236` — `commit_weights` `Pays::No`.
- `pallets/subtensor/src/macros/dispatches.rs:267-270` — `commit_mechanism_weights` `Pays::No`.
- `pallets/subtensor/src/macros/dispatches.rs:302-303` — `batch_commit_weights` `Pays::No`.
- `pallets/subtensor/src/macros/dispatches.rs:349-350` — `reveal_weights` `Pays::No`.
- `pallets/subtensor/src/macros/dispatches.rs:402-405` — `reveal_mechanism_weights` `Pays::No`.
- `pallets/subtensor/src/macros/dispatches.rs:560-561` — `batch_reveal_weights` `Pays::No`.
- `pallets/subtensor/src/macros/dispatches.rs:500-503, 2019-2020, 2120-2123` — `commit_crv3_mechanism_weights` / `commit_timelocked_weights` / `commit_timelocked_mechanism_weights` `Pays::No`.
- `pallets/subtensor/src/extensions/subtensor.rs:114-302` — `validate` branches for the weights family check only `check_weights_min_stake` (no rate-limit gate).
- `pallets/subtensor/src/extensions/subtensor.rs:381-394` — `register_network` / `associate_evm_key` DO gate the rate limit in `validate` (the contrasting precedent).
- `pallets/subtensor/src/subnets/weights.rs:804-813` — in-dispatch `ensure!(check_rate_limit …, SettingWeightsTooFast)`.
- `pallets/subtensor/src/subnets/weights.rs:93-97` — in-dispatch `ensure!(check_rate_limit …, CommittingWeightsTooFast)`.
- `pallets/subtensor/src/subnets/weights.rs:1107-1127` — `check_rate_limit` definition.
- `pallets/subtensor/src/subnets/weights.rs:922-930` — `do_set_weights` returns plain `DispatchResult` (no `actual_weight` refund).
- `pallets/subtensor/src/weights.rs:2617-2625` — benchmarked `set_weights` weight (~16.9 B-ps).
- `pallets/subtensor/src/lib.rs:750-752` — default `WeightsSetRateLimit = 100`.
- `runtime/src/lib.rs:287-308` — `MAXIMUM_BLOCK_WEIGHT` / `NORMAL_DISPATCH_RATIO`.

## Remediation

Two complementary fixes; (A) is the primary one and matches the existing precedent for `register_network` / `associate_evm_key`.

**(A) Replicate the rate limit in `validate` so over-rate weight txs are rejected before inclusion.** In each weights branch of `SubtensorTransactionExtension::validate`, after the min-stake check, resolve the caller's UID and consult `check_rate_limit` against the current block, returning `CustomTransactionError::RateLimitExceeded` on failure. Sketch for the `set_weights` branch in `pallets/subtensor/src/extensions/subtensor.rs`:

```rust
Some(Call::set_weights { netuid, .. })
| Some(Call::set_mechanism_weights { netuid, .. }) => {
    if !Self::check_weights_min_stake(who, *netuid) {
        return Err(CustomTransactionError::StakeAmountTooLow.into());
    }
    // New: mirror the in-dispatch throttle into the validity gate.
    if !Pallet::<T>::get_commit_reveal_weights_enabled(*netuid) {
        let uid = Pallet::<T>::get_uid_for_net_and_hotkey(*netuid, who)
            .map_err(|_| CustomTransactionError::HotKeyNotRegisteredInNetwork)?;
        let current_block = Pallet::<T>::get_current_block_as_u64();
        let idx = NetUidStorageIndex::from(*netuid); // use mech index for *_mechanism_weights
        if !Pallet::<T>::check_rate_limit(idx, uid, current_block) {
            return Err(CustomTransactionError::RateLimitExceeded.into());
        }
    }
    Ok((Default::default(), (), origin))
}
```

Apply the analogous guard to the `commit_weights` / `commit_mechanism_weights`, `batch_*`, and `commit_timelocked_*` / `commit_crv3_*` branches, using the correct `NetUidStorageIndex` (main vs. mechanism sub-index) for each. Note this is a best-effort pool-level reject (the pool sees `last_update` from the parent block, so two over-rate txs from the same account in the *same* block may still slip past `validate` because the pool can't observe the intra-block write); therefore keep the in-dispatch `ensure!` as the authoritative check and pair (A) with (B).

**(B) Make the spam fee-bearing.** Either drop `Pays::No` for the weights family (so spam carries a transaction fee), or — to preserve free *successful* weight-setting — return `Pays::Yes` from the dispatch on the rate-limit-failure path via `DispatchResultWithPostInfo`, so only the abusive, over-rate transactions are charged. This guarantees a cost even when (A)'s pool-level filter is bypassed by intra-block ordering.

**Regression test.** Add a test that submits two `set_weights` (and two `commit_weights`) from the same staked UID at the same block height and asserts the second is rejected by the extension's `validate` (not merely by the dispatch), and that a rate-limited dispatch reaching execution does not consume full weight for free (i.e. is `Pays::Yes` on failure). Cross-check parity with the existing `register_network` / `serve_axon` validate-path rate-limit tests.

## Verification

I independently re-verified every cited claim against source at main @ 49164bd6 (spec_version 417):

- Confirmed `set_weights` is `call_index(0)`, `DispatchClass::Normal`, `Pays::No` with `WeightInfo::set_weights()` (`dispatches.rs:84-85`), and the same shape across the full family (grep of `dispatches.rs` enumerated call indices 0, 80, 96, 97, 98, 100, 113, 115, 116, 117, 118, 119).
- Read the entire `validate` body (`subtensor.rs:99-397`) and confirmed every weights branch calls only `check_weights_min_stake` (+ reveal-window checks for reveals); no branch consults `WeightsSetRateLimit`.
- Confirmed `check_weights_min_stake` (`lib.rs:2687-2698`) is a stake eligibility gate, identical for every tx, with no per-block throttling.
- Confirmed the rate limit is enforced only in-dispatch via `ensure!` (`weights.rs:808-812` for set, `93-97` for commit), with `check_rate_limit` at `weights.rs:1107-1127` and intra-block `set_last_update_for_uid` writes (`weights.rs:855, 138`) ensuring only the first tx per UID per block succeeds.
- Confirmed `do_set_weights` returns a plain `DispatchResult` with no `PostDispatchInfo` (`weights.rs:922-930`), so `CheckWeight` issues no `actual_weight` refund and the full benchmarked weight (~16.9 B-ps, `weights.rs:2617-2625`) is consumed by failed txs.
- Confirmed the runtime extension tuple includes `CheckNonce` and `CheckWeight` (`runtime/src/lib.rs:1662-1682`), so an account can chain consecutive-nonce txs into one block, and that `pallet_shield`'s extension only gates `submit_encrypted` (`pallets/shield/src/extension.rs:51-78`), not weights.
- Confirmed the maintainers already mirror rate limits in `validate` for `register_network`, `associate_evm_key` (`subtensor.rs:381-394`), and `serve_axon` (via `validate_serve_axon`), establishing the omission for weights as an inconsistency.
- Quantified the flood: Normal budget ≈ 3.0e12 ps (`runtime/src/lib.rs:287-308`) ⇒ ~177 `set_weights` per block, all free.

**Verdict: CONFIRMED.** The vulnerability is real and exploitable as described. **Severity adjustment vs. seed:** I retain the seed's "medium" qualitative rating but assign a precise CVSS v3.1 base of **4.3 (AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)** rather than inflating it. Rationale for `A:L` (not `A:H`): the attack degrades — but does not deny — service; only the Normal dispatch class is congested, block production and the Mandatory/Operational classes (consensus liveness, governance/sudo) are unaffected, and there is a real `StakeThreshold` precondition (`PR:L`). Note that sustained cross-block flooding could be argued toward `A:H` (5.3) given the zero marginal cost; I chose the conservative `A:L` to avoid overstating impact, and flag the higher reading explicitly.

## Reproduction

**Status: REPRODUCED — passing compiled test.**

- Test: `tests::transaction_extension_pays_no::ghsa_2026_006_set_weights_paysno_validate_omits_ratelimit`
- File: `pallets/subtensor/src/tests/transaction_extension_pays_no.rs`
- Run: `SKIP_WASM_BUILD=1 cargo test -p pallet-subtensor --lib -- tests::transaction_extension_pays_no::ghsa_2026_006_set_weights_paysno_validate_omits_ratelimit --exact`

The test asserts the buggy behavior (and a contrast assertion of the safe/expected behavior); it **passes** against `main` @ `49164bd6` (spec_version 417), demonstrating the vulnerability is live.

<details>
<summary>Reproduction test source (the actual passing test)</summary>

```rust
// pallets/subtensor/src/tests/transaction_extension_pays_no.rs
// ---- GHSA-2026-006 (method: e2e) ----
#[test]
fn ghsa_2026_006_set_weights_paysno_validate_omits_ratelimit() {
    new_test_ext(0).execute_with(|| {
        let netuid = NetUid::from(1);
        let hotkey = U256::from(1);
        let coldkey = U256::from(2);

        // Subnet with commit-reveal disabled so do_set_weights runs the
        // per-neuron SetWeightsRateLimit check (weights.rs step 9).
        add_network_disable_commit_reveal(netuid, 1, 0);
        setup_reserves(
            netuid,
            1_000_000_000_000_u64.into(),
            1_000_000_000_000_u64.into(),
        );
        // Register a real neuron (uid 0) so it exists on-network and its
        // LastUpdate vector is sized for set_last_update_for_uid below.
        register_ok_neuron(netuid, hotkey, coldkey, 0);
        let uid = SubtensorModule::get_uid_for_net_and_hotkey(netuid, &hotkey).unwrap();

        // Drop the min-stake threshold to 0 so the ONLY thing that validate()
        // *could* reject for is the rate limit. This isolates the bug: the
        // min-stake mempool gate passes, and there is no rate-limit gate.
        SubtensorModule::set_stake_threshold(0);
        assert!(SubtensorModule::check_weights_min_stake(&hotkey, netuid));

        // Configure a non-zero per-neuron rate limit and mark this neuron as
        // having "just" set weights at the current block, so the next
        // set_weights is over-rate.
        SubtensorModule::set_weights_set_rate_limit(netuid, 100);
        System::set_block_number(10u64.into());
        let current_block = SubtensorModule::get_current_block_as_u64();
        let netuid_index = SubtensorModule::get_mechanism_storage_index(netuid, MechId::MAIN);
        SubtensorModule::set_last_update_for_uid(netuid_index, uid, current_block);

        // Sanity: the in-dispatch rate-limit helper now reports over-rate.
        assert!(!SubtensorModule::check_rate_limit(
            netuid_index,
            uid,
            current_block
        ));

        // Self-weight call (uids/weights == [uid]/[1]) avoids needing a
        // validator permit, so dispatch reaches the rate-limit gate.
        let call = RuntimeCall::SubtensorModule(SubtensorCall::set_weights {
            netuid,
            dests: vec![uid],
            weights: vec![1],
            version_key: 0,
        });

        // (a) set_weights is declared Pays::No -> if validate accepts it, it is
        //     included into a block for free.
        let info = call.get_dispatch_info();
        assert_eq!(info.pays_fee, frame_support::dispatch::Pays::No);

        // (b) THE BUG: SubtensorTransactionExtension::validate does NOT enforce
        //     the per-neuron SetWeightsRateLimit. An over-rate set_weights still
        //     passes validate and would be admitted to the mempool / included
        //     for free.
        assert_ok!(validate_signed(hotkey, &call));

        // (c) CONTRAST: the real dispatch path *does* enforce the rate limit and
        //     fails -> the work was only rejected after free inclusion.
        assert_err!(
            SubtensorModule::set_weights(
                RuntimeOrigin::signed(hotkey),
                netuid,
                vec![uid],
                vec![1],
                0,
            ),
            Error::<Test>::SettingWeightsTooFast
        );
    });
}
```

</details>


## References
- Source: subtensor main @ 49164bd6, spec_version 417.
- Contrasting precedent (rate limit mirrored into `validate`): `pallets/subtensor/src/extensions/subtensor.rs:381-394` (`register_network`, `associate_evm_key`) and `validate_serve_axon` usage at `subtensor.rs:315-366`.
- Related throttle storage/defaults: `WeightsSetRateLimit` (`pallets/subtensor/src/lib.rs:750-752, 2003-2004`); `StakeThreshold` (`pallets/subtensor/src/lib.rs:875, 2378`).



---

## Patch

Fixed in [`opentensor/subtensor@03a79d08e43d`](https://github.com/opentensor/subtensor/commit/03a79d08e43d) (PR [#10](https://github.com/opentensor/subtensor/pull/10)).

Live on mainnet as of **spec_version 419** (`main`).
