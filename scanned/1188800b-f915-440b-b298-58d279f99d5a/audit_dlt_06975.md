# [M] Possible DOS (out-of-gas) on loops.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-06-yieldy
Published: 2022-06-26
Source: https://github.com/code-423n4/2022-06-yieldy-findings/issues/94
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-06-yieldy/blob/main/src/contracts/BatchRequests.sol#L16
https://github.com/code-423n4/2022-06-yieldy/blob/main/src/contracts/BatchRequests.sol#L36
https://github.com/code-423n4/2022-06-yieldy/blob/main/src/contracts/BatchRequests.sol#L91


# Vulnerability details

## Impact
There is possible to get a out of gas issue while iterating the for loop.
Please take a look to this link;
https://github.com/wissalHaji/solidity-coding-advices/blob/master/best-practices/be-careful-with-loops.md

## Proof of Concept

Lets say i want to run the function on [`BatchRequests.sol#L14`](https://github.com/code-423n4/2022-06-yieldy/blob/main/src/contracts/BatchRequests.sol#L14) and i got a lot of [`contracts`](https://github.com/code-423n4/2022-06-yieldy/blob/main/src/contracts/BatchRequests.sol#L9) pending for withdrawal.



## Tools Used
Manual revision

## Recommended Mitigation Steps

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
