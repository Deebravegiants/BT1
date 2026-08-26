# [M] DOS of deposit::DLoopCoreBase function due to Insufficient Balance of debt token by 1 wei.

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-17
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/85
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** Rajeshkotaru189
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/rudhra1749)

  **Beneficiary:** 0x51060Ecc85024a1F82a47190d769a5849C889b50
  **Submission hash (on-chain):** 0x59a77670abcd3049bcaa209f112194c2408ead32fbd0d42d1ed05cc861e59895
  **Severity:** medium
  
  **Description:**
  **Description**\
Let's say a user call deposit function in DLoopCoreBase contract then it will take the collateral from user to give to lending contract and then calculate the amount it should borrow from lending contract such that it tries to maintain current leverage.
https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/blob/bef3b2af8c38552a9e697ff8eecfd9bdf3982834/contracts/vaults/dloop/core/DLoopCoreBase.sol#L764-L771
```solidity
 uint256 debtTokenAmountToBorrow = getBorrowAmountThatKeepCurrentLeverage(
                address(collateralToken),
                address(debtToken),
                supplyAssetAmount,
                currentLeverageBpsBeforeSupply > 0
                    ? currentLeverageBpsBeforeSupply
                    : targetLeverageBps
            );
```
let's say here  debtTokenAmountToBorrow =10e18.Then it calls  _borrowFromPool function.
https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/blob/bef3b2af8c38552a9e697ff8eecfd9bdf3982834/contracts/vaults/dloop/core/DLoopCoreBase.sol#L774-L778
```solidity
        _borrowFromPool(
            address(debtToken),
            debtTokenAmountToBorrow,
            address(this)
        );
```
https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/blob/bef3b2af8c38552a9e697ff8eecfd9bdf3982834/contracts/vaults/dloop/core/DLoopCoreBase.sol#L362-L404
```solidity
    function _borrowFromPool(
        address token,
        uint256 amount,
        address onBehalfOf
    ) internal {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/85_
