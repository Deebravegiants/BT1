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


_Trimmed to 38 lines — full report: https://github.com/sigp/lighthouse/security/advisories/GHSA-wm9c-xvqq-5c28_
