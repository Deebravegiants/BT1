# [M] riskPoolBalance is not used

## Summary
Severity: Medium
Contest weight: 0.0461
Dataset id: 6109
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of an accounting logic error where a portion of the funds that should be paid to a winner is diverted into a variable representing a risk pool balance, but that balance is never referenced again in the contract logic. The root cause is that the contract deducts a risk amount during each winner‑picking operation without implementing any subsequent mechanism to consume, redistribute, or return those funds. An attacker or any user can exploit this by simply triggering winner selection, causing the contract to lock away a slice of the total pool that will never be part of any future payout. The impact is that legitimate participants receive a smaller payout than expected, and the locked amount effectively disappears from the user’s perspective, leading to missing refunds or zero balances where funds should appear. This condition occurs every time the winner‑selection function is called, under normal operating conditions of the protocol. All users who rely on the contract to receive their full winnings are affected, while the contract owner retains the only possible path to retrieve the stranded funds by manually inserting the risk pool amount into a Merkle tree—a method that was not intended for this purpose and may be abused. The issue was discovered during a manual audit that compared state variable usage against the intended financial flow, noticing that the riskPoolBalance variable is written to but never read. Because the contract does not emit explicit events or revert when the risk pool is populated, the problem can be subtle and may only be observed as an unexpected shortfall in payouts, making it hard to notice without thorough state‑tracking. To remediate, the risk pool feature should either be fully implemented—providing a clear purpose such as covering slashing, insurance, or future rewards—or removed entirely to prevent dead‑money accumulation. In generic terms, this is a dead‑funds or unused‑balance bug, where money is sent to a storage slot that is never utilized, violating the accounting assumptions of the protocol and breaking the expectation that all deposited funds will eventually be distributed to participants.

## Recommendation
Consider removing risk pool or completing the feature for which risk pool was introduced.
