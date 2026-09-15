# [M] Potential Out of Gas due to unbounded loop in `refund` function

## Summary
Severity: Medium
Chain: Smart contract
Component: DAOsis
Published: 2025-01-28
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/2
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/chainNue)

  **Beneficiary:** 0xABCDE0360aBCbA45098125E55437B005aE5DF46F
  **Submission hash (on-chain):** 0xaec163bf08b7ee9d57411648e0175f70cfb62556df539f9cdc7651cc88030b86
  **Severity:** medium
  
  **Description:**
  **Description**\
The `refund` function is vulnerable to out-of-gas errors due to the unbounded loop iterating over the `participants` array. If the number of `participants` grows significantly (e.g., 400–1000 or more), the gas required to process the loop will likely exceed the block gas limit, causing the function to fail and rendering the refund process unusable.

```js
    // refund Token
    function refund() external onlyOwner whenNotPaused {
        require(block.timestamp > endTime, "IDO sale has not ended yet");
        require(totalRaised < maxCap, "IDO successful, no refunds!");

@>      for (uint256 i = 0; i < participants.length; i++) {
            address user = participants[i];
            uint256 userContribution = userDetails[user].buyAmount;

            if (userContribution > 0) {
                userDetails[user].buyAmount = 0; 
                (bool success, ) = payable(user).call{value: userContribution}("");
                require(success, "Refund transfer failed");

                emit Refund(user, userContribution);
            }
        }
    }
```

**Attack Scenario**\
1. The buy function appends new addresses to the participants array using participants.push(msg.sender);.
2. There is no cap or limit on the number of participants allowed in the sale.
3. If the participants array grows excessively large due to high participation, calling the refund function will result in an out-of-gas error because the loop tries to process all participants in a single transaction.

This scenario prevents the refund process from completing, locking funds in the contract indefinitely.

**Mitigation:**
To address this issue, the refund function should be revised to process participants in smaller batches using a range parameter. This allows refunds to be handled incrementally, avoiding gas limit constraints.

```js
function refund(uint256 start, uint256 end) external onlyOwner whenNotPaused {
    require(block.timestamp > endTime, "IDO sale has not ended yet");
    require(totalRaised < maxCap, "IDO successful, no refunds!");
    require(start < end && end <= participants.length, "Invalid range");

    for (uint256 i = start; i < end; i++) {
        address user = participants[i];
        uint256 userContribution = userDetails[user].buyAmount;

        if (userContribution > 0) {
            userDetails[user].buyAmount = 0; 
            (bool success, ) = payable(user).call{value: userContribution}("");
            require(success, "Refund transfer failed");

            emit Refund(user, userContribution);
        }
    }
}
```
