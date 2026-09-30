# [M] (previously M-02 in fix review)

## Summary
Severity: Medium
Contest weight: 0.0390
Dataset id: 19684
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a conditional branch that treats a price‑feed phase as empty when the stored startingRoundId equals zero. In the current implementation the constructor or initialization logic guarantees that startingRoundId is always set to a non‑zero value, so the condition can never be true. The root cause is an assumption in the code that a zero startingRoundId is a possible state, even though the surrounding logic enforces a non‑zero invariant. If, contrary to the design, startingRoundId were ever zero, the contract would consider the phase empty, potentially returning a default price of zero or triggering a revert when callers request the latest round data. This could cause downstream protocols that rely on the oracle to receive an unexpected zero price, fail their own calculations, or halt execution, leading to user‑visible symptoms such as missing price updates, failed transactions, or funds being locked because a trade cannot be priced. The vulnerability manifests only under the unreachable condition where startingRoundId is zero, which does not occur in the deployed code, making it hard to observe in testing. It was discovered during a systematic audit that flagged the empty‑phase check as a potential logical error. Because the branch is never exercised, the issue may be overlooked unless the code is closely examined for invariant violations. The recommended remediation is to remove the unreachable check or replace it with an explicit assert that startingRoundId is never zero, thereby eliminating dead code and clarifying the contract’s assumptions. Conceptually, this is a defensive‑programming flaw where an impossible state is handled as if it were valid, which can lead to incorrect accounting or denial‑of‑service if the invariant were ever broken.

## Recommendation
Although this appears to be an unreachable state since in the current implementation, startingRoundId cannot be 0 and therefore the phase can’t be empty.
Fix confirmed.
