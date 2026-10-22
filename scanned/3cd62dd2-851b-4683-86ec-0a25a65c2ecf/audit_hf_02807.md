# [M] Lack of check on `mustStartAtOrAfter`

## Summary
Severity: Medium
Contest weight: 0.6264
Dataset id: 15336
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability arises from the absence of a validation check on the `_mustStartAtOrAfter` parameter when configuring a new funding cycle in the Juicebox protocol. This parameter is intended to enforce that a newly proposed funding cycle cannot become active until a predefined ballot waiting period has elapsed. Because the contract does not verify that `_mustStartAtOrAfter` fits within the expected `uint56` range or that it represents a future timestamp, a malicious or careless project owner can supply the maximum possible `uint56` value (`type(uint56).max`). When this oversized value is packed into the bit‑field that stores the funding cycle’s start time, the shift operation overflows and effectively sets the start time to a value that is interpreted as being in the past. Consequently, the contract treats the newly configured funding cycle as the current one immediately, bypassing the ballot delay that should have prevented instant activation. This flaw can be exploited by invoking the `configureFor` function of `JBFundingCycleStore` with a crafted funding cycle where only `mustStartAtOrAfter` is set to the extreme value, as demonstrated in the proof‑of‑concept test. The impact is that the protocol’s governance model is undermined: contributors and other stakeholders expect a three‑day (or otherwise configured) waiting period for review and possible objection, but the owner can instantly change key parameters such as funding duration, payout splits, or reserved tokens without community oversight. Users may notice that a funding cycle appears to start right away, contrary to the UI indication of a pending ballot, leading to confusion, loss of trust, and potential misallocation of contributed funds. The issue was discovered during a Code4rena audit when the auditors modified the `mustStartAtOrAfter` field to its maximum value and observed that the ballot waiting time was effectively ignored. The problem is subtle because the overflow happens during internal bit‑packing, so external observers see a normal start timestamp field, making the bug hard to spot without deep inspection of the packing logic. To remediate the issue, the contract should enforce a sanity check on `_mustStartAtOrAfter`, ensuring it does not exceed the maximum allowable `uint56` value and that it represents a timestamp that is at least the current block timestamp and respects the ballot’s configured delay. By adding this validation, the protocol can guarantee that funding cycles cannot be started retroactively or instantly, preserving the intended governance delay and protecting contributors from unauthorized, immediate reconfigurations.

## Proof of Concept
The [proof of concept](https://gist.github.com/zzzitron/a8c6067923a87af8e001c05442258370#file-2022-07-juiceboxv2-t-sol-L77-L115) is almost the same as [`TestReconfigure::testReconfigureProject`](https://github.com/jbx-protocol/juice-contracts-v2-code4rena/blob/828bf2f3e719873daa08081cfa0d0a6deaa5ace5/contracts/system_tests/TestReconfigure.sol#L77-L114). In the original test, the owner of the project is reconfiguring funding cycle, but it is not in effect immediately because ballot is set. Only after 3 days the newly set funding cycle will be the current one.

In the above proof of concept, only one parameter of the funding cycle is modified: `mustStartAtOrAfter` is set to `type(uint56).max`. As the result, the newly set funding cycle is considered as the current one without waiting for the ballot.

The cause of this is missing check on `mustStartAtOrAfter` upon setting [here](https://github.com/jbx-protocol/juice-contracts-v2-code4rena/blob/828bf2f3e719873daa08081cfa0d0a6deaa5ace5/contracts/JBFundingCycleStore.sol#L306-L312). If the given `_mustStartAtOrAfter` is huge, it will be passed eventually to the `_initFor`, `_packAndStoreIntrinsicPropertiesOf`. Then it will ‘overflow’ by shifting and set to the funding cycle, which [essentially can be set to any value including the past](https://github.com/jbx-protocol/juice-contracts-v2-code4rena/blob/828bf2f3e719873daa08081cfa0d0a6deaa5ace5/contracts/JBFundingCycleStore.sol#L518-L522). Also, it seems like the number will be also effected because the bigger digit will carry over.
```solidity
// in JBFundingCycleStore::_packAndStoreIntrinsicPropertiesOf
// where the `_start` is derived from `_mustStartAtOrAfter`

// start in bits 144-199.
packed |= _start << 144;

// number in bits 200-255.
packed |= _number << 200;
```

## Recommendation
Add a check for the `_mustStartAtOrAfter`:
```solidity
// example check for _mustSTartAtOrAfter
// in JBFundingCycleStore::configureFor

if (_mustStartAtOrAfter > type(uint56).max) revert INVALID_START();
```
Good catch!

**drgorillamd (Juicebox) resolved:**

PR with fix: [PR #1](https://github.com/jbx-protocol/juice-contracts-v3/pull/1)

**berndartmueller (warden) reviewed mitigation:**

`mustStartAtOrAfter` and the start date of an upcoming funding cycle are now validated to fit in `uint56`.
