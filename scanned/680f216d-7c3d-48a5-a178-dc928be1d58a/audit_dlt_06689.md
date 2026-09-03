# [H] a fake `dLoopCore` contract can steal leftover funds in `DLoopDepositorBase` because `DLoopDepositorBase::deposit()` does not restrict any `dLoopCore`input

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-27
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/279
Type: hats-finding

## Details
**Github username:** @CoheeYang
  **Twitter username:** @CoheeHimself
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/CoheeYang)

  **Beneficiary:** 0x9280209B3c436FEaA0e00A7eacEd4d75F7E4b2dC
  **Submission hash (on-chain):** 0x143b4e00bb1c58b3c7122e5dbd3f497e6c89dfcaa041f7b3e43b567565854a54
  **Severity:** high
  
  **Description:**
  ## **Description**

[DLoopDepositorBase::deposit()](https://github.com/dtrinity/sonic-solidity-contracts/blob/1844b73f78f0179228303d205271d510339e446b/contracts/vaults/dloop/periphery/DLoopDepositorBase.sol#L253-L353) does not restrict any `dLoopCore`address input,


```solidity
    function deposit(
        uint256 assets, // deposit amount
        address receiver,
        uint256 minOutputShares,
        bytes calldata debtTokenToCollateralSwapData,
        DLoopCoreBase dLoopCore
    ) public nonReentrant returns (uint256 shares) {
        ERC20 collateralToken = dLoopCore.collateralToken();
        ERC20 debtToken = dLoopCore.debtToken();

        // Transfer the collateral token to the vault (need the allowance before calling this function)
        // The remaining amount of collateral token will be flash loaned from the flash lender
        // to reach the leveraged amount
        collateralToken.safeTransferFrom(msg.sender, address(this), assets);

        // Calculate the estimated overall slippage bps
        uint256 estimatedOverallSlippageBps = _calculateEstimatedOverallSlippageBps(
                dLoopCore.convertToShares(dLoopCore.getLeveragedAssets(assets)),
                minOutputShares
            );

        // Make sure the estimated overall slippage bps does not exceed 100%
        if (
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/279_
