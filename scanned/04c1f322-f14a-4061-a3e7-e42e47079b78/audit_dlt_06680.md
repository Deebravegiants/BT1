# [H] Incorrect Collateral Transfer Logic Allows DOS in `DLoopDecreaseLeverageBase.sol`

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-07-04
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/324
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** @sr199812151
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/ShawnAudit)

  **Beneficiary:** 0x1cEc7BD7e869c6E9690381bc22259563e1Efa62C
  **Submission hash (on-chain):** 0x8d952cef3b3a42885517fface3b7635ef7536656f9478ee4280e3fe449fef2bb
  **Severity:** high
  
  **Description:**
  **Description**\

In the `DLoopDecreaseLeverageBase.sol` contract, there is a critical flaw in the logic that handles the transfer of leftover collateral tokens after a leverage decrease operation. Specifically, the contract first transfers all remaining collateral tokens to the `dLoopCore` contract, and then attempts to transfer the user's entitled collateral to the receiver. However, since the contract's balance is already depleted by the first transfer, the second call will revert, causing DOS.

```solidity
// ... existing code ...
uint256 leftoverAmount = collateralToken.balanceOf(address(this));
if (
    // ... some condition ...
) {
    collateralToken.safeTransfer(address(dLoopCore), leftoverAmount);
    emit LeftoverCollateralTokensTransferred(
        // ... event params ...
    );
}
// @audit
collateralToken.safeTransfer(msg.sender, receivedCollateralTokenAmount);
// ... existing code ...
```



**Attack Scenario**\

1. A user initiates a leverage decrease operation, expecting to receive a certain amount of collateral tokens as a result.
2. The contract executes the following logic:
    - Transfers all remaining collateral tokens to the `dLoopCore` contract.
    - Attempts to transfer the user's entitled collateral to the receiver.
3. Since the contract's balance is now zero, the transfer to the receiver fails.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/324_
