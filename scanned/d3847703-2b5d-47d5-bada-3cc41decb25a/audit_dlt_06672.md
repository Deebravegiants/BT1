# [M] Refund function can be halted completely by malicious user (contract) by reverting

## Summary
Severity: Medium
Chain: Smart contract
Component: DAOsis
Published: 2025-01-28
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/25
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/chainNue)

  **Beneficiary:** 0xABCDE0360aBCbA45098125E55437B005aE5DF46F
  **Submission hash (on-chain):** 0x8be437055b0f19f4aa8e6e279cceabc379058c2cc92f61e825bd89063113987f
  **Severity:** medium
  
  **Description:**
  **Description**

In refund, there is a check need to be successfully passed `require(success, "Refund transfer failed");` otherwise the `refund` can't be processed.

```js
    // refund Token
    function refund() external onlyOwner whenNotPaused {
        require(block.timestamp > endTime, "IDO sale has not ended yet");
        require(totalRaised < maxCap, "IDO successful, no refunds!");

        for (uint256 i = 0; i < participants.length; i++) {
            address user = participants[i];
            uint256 userContribution = userDetails[user].buyAmount;

            if (userContribution > 0) {
                userDetails[user].buyAmount = 0; 
                (bool success, ) = payable(user).call{value: userContribution}("");
@>              require(success, "Refund transfer failed");

                emit Refund(user, userContribution);
            }
        }
    }
```

If a malicious contract is included in the participants array and the `refund()` function attempts to send Ether to this contract, the malicious contract can stall the refund process by exploiting the following vulnerabilities:

1. Gas Exhaustion Attack


_Trimmed to 38 lines — full report: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/25_
