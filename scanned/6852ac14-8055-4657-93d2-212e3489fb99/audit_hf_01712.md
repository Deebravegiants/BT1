# [M] M-5 Lack of verification for the native ETH balance and staking balance in the

## Summary
Severity: Medium
Contest weight: 0.0411
Dataset id: 9342
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a missing verification step for the native ETH balance and the staking balance of an eigenPod when the removeNodeDelegatorContractFromQueue function is executed. Because the function does not assert that the pod’s ETH holdings or its recorded staking amount are non‑zero or consistent, the protocol can continue to calculate the price of the derivative token RSETH using stale or incorrect balance data. This occurs whenever a delegator contract is removed from the queue, which is a normal maintenance operation, but the lack of a balance check means that a pod that has already withdrawn its ETH or whose staking balance has been reduced to zero can still be processed. An attacker or a careless operator can trigger the function on such a pod, causing the aggregate accounting of total ETH staked versus total RSETH supply to become mismatched. The price oracle that derives RSETH price from the ratio of total ETH balance to total RSETH supply will then output a value that deviates from the true market value. Users who later mint or redeem RSETH may receive fewer tokens than expected, see their balances shrink unexpectedly, or be offered an inflated price that later collapses, leading to potential loss of funds. The issue was discovered during a systematic audit by MixBytes, which identified the logical flaw that the function does not perform a zero‑balance guard. The problem is subtle because the price discrepancy may only become apparent after several removals, making it hard to trace back to a single missing check. To remediate, the function should explicitly verify that both the native ETH balance and the recorded staking balance of the eigenPod are greater than zero and consistent before proceeding, and revert the transaction if the check fails. This type of bug belongs to the class of unchecked invariants or missing state validation, where critical accounting variables are assumed to be valid without enforcement, leading to accounting breaks and incorrect token pricing. From a user’s perspective, the symptoms may appear as a sudden drop in the displayed RSETH price, a refund that returns zero ETH, or a balance that becomes zero after a redemption, contrary to the expectation that the protocol always returns the correct proportional amount of ETH.

## Recommendation
We recommend checking zero balance during the removeNodeDelegatorContractFromQueue function.
