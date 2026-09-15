# [H] Incorrect processing of effective balances in Electra epoch processing

## Summary
Severity: High
Chain: Ethereum
Component: sigp/lighthouse
Published: 2025-04-01
Source: https://github.com/sigp/lighthouse/security/advisories/GHSA-wm9c-xvqq-5c28
Type: github-advisory

## Details
Lighthouse versions `v7.0.0-beta.0` to `v7.0.0-beta.4` contain a bug in the implementation of `process_epoch` which affects all Electra-enabled networks. If you are running validators on an Electra network, you **must** upgrade them to `v7.0.0-beta.5` or newer.

We are grateful to [`@alexfilippov314`](https://x.com/alexfilippov314) for reporting this vulnerability as part of the [Pectra security competition](https://cantina.xyz/competitions/1845d0b1-1d2b-42be-b347-a866d6549fca) coordinated by The Ethereum Foundation and Cantina. Thankfully, the bug does not impact Ethereum mainnet.

## Severity

The severity of this bug is **High**, based on it being High impact and High likelihood. If this bug were exploited by an attacker it could be used to split Lighthouse nodes from the canonical chain. Around 1/3 of validators run Lighthouse, so the chain would likely stop finalizing if this were to occur. The difficulty of exploiting this vulnerability is low for a sophisticated attacker, it just requires carefully timed withdrawal and consolidation operations.

## Details

The bug was caused by an incorrect assumption in Lighthouse's implementation of _single-pass epoch processing_. Single-pass epoch processing was [originally introduced in 2023](https://ethresear.ch/t/formally-verified-optimised-epoch-processing/17359) for the Capella spec as we prepared to migrate Lighthouse to [persistent data structures](https://blog.sigmaprime.io/tree-states-part1.html). We shipped the first version of the algorithm without issue in Lighthouse v5.2.0 in June 2024.

The bug was introduced during the adaption of single-pass for Electra, which required extensive changes to epoch processing in order to implement "MaxEB" ([EIP-7521](https://eips.ethereum.org/EIPS/eip-7251)). Single-pass epoch processing was made possible by a key insight about prior versions of the epoch processing spec: the updates for a validator `i` do not depend on the updates for any other validator `j`, and so they can be reordered (or parallelised). This property of the spec is no longer true as of Electra, due to the introduction of _consolidations_.

A consolidation allows one validator (`i`) to exit the network, transferring its balance to another existing validator (`j`). Our initial attempt to make this play nicely with single-pass epoch processing was to "patch up" the effective balances for all validators affected by consolidations, by _rerunning_ `process_effective_balance_updates` for each validator index.

This seemed sound, because `process_effective_balance_updates` is the only part of per-validator epoch processing which is dependent on the processing of consolidations, as shown below:

```python
def process_epoch(state: BeaconState) -> None:
    process_justification_and_finalization(state)
    process_inactivity_updates(state)
    process_rewards_and_penalties(state)
    process_registry_updates(state)  # [Modified in Electra:EIP7251]
    process_slashings(state)  # [Modified in Electra:EIP7251]
    process_eth1_data_reset(state)
    process_pending_deposits(state)  # [New in Electra:EIP7251]
    process_pending_consolidations(state)  # [New in Electra:EIP7251]
    process_effective_balance_updates(state)  # [Modified in Electra:EIP7251]
    process_slashings_reset(state)
    process_randao_mixes_reset(state)
    process_historical_summaries_update(state)
    process_participation_flag_updates(state)
    process_sync_committee_updates(state)
```

The other processing that occurs after `process_effective_balance_updates` all relates to global state, and was never part of the single-pass loop in the first place.

The problem is, `process_effective_updates` produces different results when it is run multiple times, compared to when it is run once. To quote directly from `@alexfilippov314`'s discloure:

> The issue arises because updating the effective balance twice does not necessarily produce the same result as a single update due to hysteresis:

```python
def process_effective_balance_updates(state: BeaconState) -> None:
    # Update effective balances with hysteresis
    for index, validator in enumerate(state.validators):
        balance = state.balances[index]
        HYSTERESIS_INCREMENT = uint64(EFFECTIVE_BALANCE_INCREMENT // HYSTERESIS_QUOTIENT)
        DOWNWARD_THRESHOLD = HYSTERESIS_INCREMENT * HYSTERESIS_DOWNWARD_MULTIPLIER
        UPWARD_THRESHOLD = HYSTERESIS_INCREMENT * HYSTERESIS_UPWARD_MULTIPLIER
        # [Modified in Electra:EIP7251]
        max_effective_balance = get_max_effective_balance(validator)

        if (
            balance + DOWNWARD_THRESHOLD < validator.effective_balance
            or validator.effective_balance + UPWARD_THRESHOLD < balance
        ):
            validator.effective_balance = min(balance - balance % EFFECTIVE_BALANCE_INCREMENT, max_effective_balance)

```

> For example, if the initial balance is 64 ETH, and we process a balance decrease of 32 ETH followed by increase of 31.9 ETH, the outcome depends on how many times the effective balance is updated:
>
> * Single Update (Correct Behavior): The net decrease of 0.1 ETH does not meet the DOWNWARD_THRESHOLD, so the effective balance remains 64 ETH.
> * Multiple Updates (Incorrect Behavior): If the effective balance is updated twice, both balance changes trigger an update. The second update sets the effective balance to 63 ETH because a balance of 63.9 ETH does not justify an effective balance of 64 ETH.
>
> Consider the following scenario
>
> 1. There are two validators, A and B, where A has a balance of 31.9 ETH (validator can still be active with such balance) and B has a balance of 64 ETH.
> 2. B submits a partial withdrawal request for 32 ETH.
> 3. Around the same time, A submits a consolidation request to transfer its balance to B (A → B).
> 4. This situation is possible because the `process_consolidation_request` function does not check whether the target validator has any pending withdrawals.
> 5. It is also possible for both the partial withdrawal and the consolidation processing to occur within the same epoch. This means that before epoch processing, the balance of validator B is 32 ETH (since partial withdrawal was already processed), while the effective balance remains 64 ETH.
> 6. In such situation, according to the spec, B’s effective balance after epoch processing should remain 64 ETH because the balance decrease of 0.1 ETH does not meet the threshold required to trigger an effective balance update due to hysteresis.
> 7. However, in Lighthouse, the outcome differs due to multiple effective balance updates. First, Lighthouse reduces B’s effective balance to 32 ETH before processing the consolidation request. Then, after consolidation, it updates B’s effective balance to 63 ETH because the new balance of 63.9 ETH does not justify an effective balance of 64 ETH.

## The Fix

The fix is to ensure that effective balance processing only occurs once for each validator index. This change was made in [PR#7209](https://github.com/sigp/lighthouse/pull/7209) and released as part of `v7.0.0-beta.5`.

To maintain some of the benefits of single-pass epoch processing, we continue to process effective balance updates for all validators unaffected by consolidations inside the single-pass loop. For all affected validators, we ensure that _all_ consolidations are processed before updating their effective balances. This is more similar to how the spec sequences these operations, and  also ensures that each validator's effective balance is only updated once per epoch transition.

The fix was complicated slightly by one of our caches, the `PreEpochCache`. This cache contains a vector of effective balances and expects there to be an entry to each validator pushed as part of the single-pass loop. Fortunately, this cache can gracefully handle effective balance changes made during epoch processing, so our solution initially pushes the old effective balance for each validator affected by a consolidation, and then corrects this once `process_effective_balance_updates` is run for that validator.

## Further Considerations

We will be increasing testing and fuzzing efforts of our Electra code in the lead up to shipping Electra on mainnet.

A new spec test has already been [contributed upstream](https://github.com/ethereum/consensus-specs/pull/4239) to `consensus-specs` by Justin Traglia. This spec test will be added to our fuzzing corpus, so that the fuzzer may discover  novel code paths. We will be using an approach of Fault Injection to ensure that the fuzzer has sufficient corpus coverage to explore all of the corners of Electra epoch processing. These changes will also benefit the security and correctness of other consensus clients, as the upstream spec tests are consumed by all clients, and our fuzzer differentially fuzzes all of the clients against each other.

We are also planning to update the paper proofs in [verified-consensus](https://github.com/sigp/verified-consensus) so that they cover the changes we have made for Electra. This may take several weeks, as the changes to epoch processing are the most extensive since the Altair fork many years ago.

## Thanks

We are grateful to `high-byte` at Cantina for bringing the vulnerability report to our attention, Justin Traglia for discussion and testing assistance, and most of all `@alexfilippov314` for responsibly disclosing this vulnerability and helping to secure Ethereum!
