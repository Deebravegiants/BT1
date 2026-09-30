# [M] Possible DOS

## Summary
Severity: Medium
Contest weight: 0.4017
Dataset id: 13208
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an unbounded iteration over a dynamic array of contract addresses within a public withdrawal function, which can cause the transaction to run out of gas and revert. The root cause is that the for‑loop does not limit the number of iterations based on the block gas limit, and each iteration performs an external call to a staking contract. As the array of contracts grows, the cumulative gas required to process all entries may exceed the gas stipend supplied by the caller, leading to an out‑of‑gas exception. An attacker or even honest users can exploit this by populating the contracts array with a large number of entries, or by simply waiting for the natural growth of the list, and then invoking the withdrawal function with a range that includes many elements. When the transaction reverts, the intended withdrawal does not occur, leaving funds effectively frozen in the staking contracts. The impact is a denial‑of‑service condition where users expect to receive their withdrawn tokens but instead see no change in their balances; the UI may display a generic transaction failure without indicating the underlying looping issue. This condition manifests whenever the caller attempts to process a batch that exceeds the practical gas limit, such as when the ‘from’ and ‘to’ indices span a large segment of the contracts array. The affected parties are any participant who relies on the batch withdrawal mechanism – typically stakers, delegators, or the protocol’s treasury. The issue was identified during a manual audit that highlighted the loop pattern as a known anti‑pattern for gas‑heavy operations. It is difficult to notice because the function works correctly for small batches and only fails when the array becomes sufficiently large, which may not be apparent during initial testing. The bug belongs to the class of “unbounded loop leading to gas exhaustion” and violates the protocol’s accounting assumption that a batch withdrawal should complete atomically. The recommended mitigation is to replace the single unbounded loop with a bounded, range‑based iteration that allows the caller to specify a safe slice of the array, or to implement a pull‑based pattern where each contract can be processed in separate transactions, thereby avoiding a single point of failure.

## Proof of Concept
Let’s say I want to run the function on [`BatchRequests.sol#L14`](https://github.com/code-423n4/2022-06-yieldy/blob/main/src/contracts/BatchRequests.sol#L14) and I got a lot of [`contracts`](https://github.com/code-423n4/2022-06-yieldy/blob/main/src/contracts/BatchRequests.sol#L9) pending for withdrawal.

## Recommendation
Use this pattern;
```solidity
/**
    @notice sendWithdrawalRequests on all addresses in contracts
 */
function sendWithdrawalRequests(uint256 from, uint256 to) external {
    uint256 contractsLength = contracts.length;
    require(from < contractsLength, "Invalid from");
    require(to <= contractsLength, "Invalid to");
    for (uint256 i = from; i < to; ) {
        if (
            contracts[i] != address(0) &&
            IStaking(contracts[i]).canBatchTransactions()
        ) {
            IStaking(contracts[i]).sendWithdrawalRequests();
        }
        unchecked {
            ++i;
        }
    }
}
```
