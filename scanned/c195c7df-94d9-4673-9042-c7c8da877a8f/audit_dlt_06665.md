# [M] Discrepancy in Token Allocation for IDO

## Summary
Severity: Medium
Chain: Smart contract
Component: DAOsis
Published: 2025-01-28
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/58
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/0x0bserver)

  **Beneficiary:** 0x88cBcd44a23Dc16dF47f144f6f6E111DB7433b71
  **Submission hash (on-chain):** 0x8b8c0c3867c4b84ce17ad0ee1ee4beaea1bbad885ae1eaf030db721d5dc5b9ba
  **Severity:** medium
  
  **Description:**
  **Description**\
As per the DAOSIS documentation, 55% of the token supply should be allocated to the IDO. However, the implementation in the `MasterFastIDO` and `MasterNormalIDO` contracts sends only 45% of the token supply to the IDO. This discrepancy deviates from the intended goal outlined in the protocol's documentation.

**Impact**\
This issue misaligns with the protocol's stated objectives, leading to incorrect token distribution and potential loss of trust from the community and investors.

**Instance**\
Present in the `constructor` of both the contract:
```javascript
        if (!feesInToken) {
@>            adminAmount = (tokenParams.tokenSupply * 55) / 100;
@>            idoAmount = tokenParams.tokenSupply - adminAmount;
            (bool success, ) = feeReceiver.call{value: deploymentFee}("");
            require(success, "Fee transfer failed!");
        } else {
@>            adminAmount = (tokenParams.tokenSupply * 54) / 100;
            feeAmount = (tokenParams.tokenSupply * 1) / 100;
@>            idoAmount = tokenParams.tokenSupply - (adminAmount + feeAmount);
        }
        token.transfer(
            admin,
            adminAmount * 10**uint256(tokenParams.tokenDecimal)
        );
```

**Fix**\
Add this in the `contructor` of both the contract:
```javascript
        if (!feesInToken) {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/58_
