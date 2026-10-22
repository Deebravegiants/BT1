# [H] Referrer can drain `ReferralFeePoolV0`

## Summary
Severity: High
Contest weight: 0.7247
Dataset id: 1032
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the reward‑claiming routine of the ReferralFeePoolV0 contract. The function that allows a referrer to claim a reward for referring users fails to update the internal accounting after a payout. Specifically, the contract records the amount owed to each referrer in a mapping but never subtracts the claimed amount from that balance nor resets the balance to zero when the claim is executed. As a result, the same reward amount remains recorded as claimable, enabling the referrer to invoke the claim function repeatedly and drain the total fee pool. The root cause is an improper state transition: the contract does not enforce a decrease of the reward balance after a successful transfer, violating basic accounting invariants that a claimed amount must be removed from the creditor’s ledger. Exploitation is straightforward – a malicious referrer can call the claim function in a loop, each call receiving the full amount that was originally allocated to them, while the contract’s total pool is reduced each time until it reaches zero. The impact is a complete loss of referral fees that were intended to be distributed among participants, potentially emptying the pool and depriving honest referrers of any compensation. This condition occurs whenever a referrer invokes the claimRewardAsMochi function; there is no guard or check that prevents subsequent calls after the first successful claim. The affected parties include the protocol that relies on referral incentives, the referrers who expect a single payout, and any users whose referral rewards are effectively stolen. The issue was discovered during a static analysis audit that compared the function’s external effects (a token transfer) with its internal state changes and noticed the absence of a balance decrement. It can be hard to notice because the function appears to succeed – the transaction does not revert and the referrer receives the tokens, giving the impression of correct behavior, while the hidden accounting error silently accumulates. The correct mitigation is to update the rewards mapping after each payout, typically by subtracting the claimed amount from the stored balance and resetting the user’s pending reward to zero, thereby restoring the invariant that total pending rewards equal the sum of individual balances. In broader terms, this is an instance of an accounting or state‑management bug where a contract fails to synchronize external token transfers with internal ledger updates, leading to double‑spending of allocated funds. From a user’s perspective, a referrer sees repeated reward payouts that should have occurred only once, while other participants notice that their referral pool is depleted and that expected refunds or incentives never materialize. The discrepancy between the expected single payout and the reality of multiple claims constitutes a breach of the protocol’s business logic and financial guarantees.

## Proof of Concept
Did not reduce user reward balance at L28-47 in [ReferralFeePoolV0.sol](https://github.com/code-423n4/2021-10-mochi/blob/main/projects/mochi-core/contracts/feePool/ReferralFeePoolV0.sol)

## Recommendation
Add the following lines
```solidity
rewards -= reward[msg.sender]; reward[msg.sender] = 0;
```
