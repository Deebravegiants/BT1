# [M] `flashProof` is not flash-proof

## Summary
Severity: Medium
Contest weight: 0.1690
Dataset id: 350
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `flashProof` modifier is supposed to prevent flash-loan attacks by disallowing performing several sensitive functions in the same block.

However, it performs this check on `tx.origin` and not on an individual user address basis. This only prevents flash loan attacks from happening within a single transaction.

But flash loan attacks are theoretically not limited to the same transaction but to the same block as miners have full control of the block and include several vulnerable transactions back to back. (Think transaction _bundles_ similar to flashbot bundles that most mining pools currently offer.)

A miner can deploy a proxy smart contract relaying all contract calls and call it from a different EOA each time bypassing the `tx.origin` restriction.

The `flashProof` modifier does not serve its purpose.

Recommend trying to apply the modifier to individual addresses that interact with the protocol instead of `tx.origin`.

Furthermore, attacks possible with flash loans are usually also possible for whales, making it debatable if adding flash-loan prevention logic is a good practice.

Flash loans with the help of miners _was not intended to be countered_ , although a check for `msg.sender` AND `tx.origin` will be applied.

## Recommendation
No recommendation
