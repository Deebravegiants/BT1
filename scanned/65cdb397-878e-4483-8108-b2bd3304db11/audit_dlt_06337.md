# [M] Vulnerability in pooledDeposit Function Enables Denial of Service (DoS) Attack

## Summary
Severity: Medium
Chain: Smart contract
Component: Blast-Futures-Exchange
Published: 2024-02-07
Source: https://github.com/hats-finance/Blast-Futures-Exchange-0x97895c329b950755566ddcdad3395caaea395074/issues/47
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** @recursiveAudit
**Submission hash (on-chain):** 0xdc4c563b13ebcebd7a558df1c5dd3a4917e84ab4e51d486623be04def381667c
**Severity:** medium

**Description:**
**Description**\
 function named `PoolDeposit:pooledDeposit()` that accepts an array of contributions (Contribution[]). This function aggregates the total amount of contributions and then transfers the total amount to a designated address (rabbit). However, there's a vulnerability in the code due to the lack of limit on the size of the contributions array, combined with the function's external visibility.

**Attack Scenario**\
Denial of Service (DoS) Attack: An attacker exploits the vulnerability by calling the `PoolDeposit:pooledDeposit()` function with an excessively large contributions array. Since the function's visibility is external, it can be called by anyone. The attacker sends a huge array of contributions, causing the function to iterate through the array in a loop.

As the function iterates through the large array, it consumes significant gas for each iteration. With a sufficiently large array, the gas cost of processing the loop exceeds the block gas limit, leading to a denial of service condition.

Impact: The excessive gas consumption prevents legitimate transactions from being processed.

**Attachments**

1. **Proof of Concept (PoC) File**

```javascript
function pooledDeposit(Contribution[] calldata contributions) external {
        uint256 poolId = allocatePoolId();
        uint256 totalAmount = 0;
        for (uint i = 0; i < contributions.length; i++) {
            Contribution calldata contribution = contributions[i];
            uint256 contribAmount = contribution.amount;
            totalAmount += contribAmount;
            require(contribAmount > 0, "WRONG_AMOUNT");
            require(totalAmount >= contribAmount, "INTEGRITY_OVERFLOW_ERROR");
            uint256 depositId = allocateDepositId();
            emit Deposit(depositId, contribution.contributor, contribAmount, poolId); //
        }
        require(totalAmount > 0, "WRONG_AMOUNT");
        emit PooledDeposit(poolId, totalAmount);
        bool success = makeTransferFrom(msg.sender, rabbit, totalAmount);
        require(success, "TRANSFER_FAILED");
    }
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Blast-Futures-Exchange-0x97895c329b950755566ddcdad3395caaea395074/issues/47_
