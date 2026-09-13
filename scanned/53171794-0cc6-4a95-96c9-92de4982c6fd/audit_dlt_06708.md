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
        // At this step, we assume that the funds from the depositor are already in the vault


        uint256 tokenBalanceBeforeBorrow = ERC20(token).balanceOf(onBehalfOf);


        _borrowFromPoolImplementation(token, amount, onBehalfOf);


        uint256 tokenBalanceAfterBorrow = ERC20(token).balanceOf(onBehalfOf);
        if (tokenBalanceAfterBorrow <= tokenBalanceBeforeBorrow) {
            revert TokenBalanceNotIncreasedAfterBorrow(
                token,
                tokenBalanceBeforeBorrow,
                tokenBalanceAfterBorrow,
                amount
            );
        }


        // Allow a 1-wei rounding tolerance when comparing the observed balance change with `amount`
        uint256 observedDiffBorrow = tokenBalanceAfterBorrow -
            tokenBalanceBeforeBorrow;
        if (observedDiffBorrow > amount) {
            if (observedDiffBorrow - amount > BALANCE_DIFF_TOLERANCE) {
                revert UnexpectedBorrowAmountFromPool(
                    token,
                    tokenBalanceBeforeBorrow,
                    tokenBalanceAfterBorrow,
                    amount
                );
            }
        } else {
            if (amount - observedDiffBorrow > BALANCE_DIFF_TOLERANCE) {
                revert UnexpectedBorrowAmountFromPool(
                    token,
                    tokenBalanceBeforeBorrow,
                    tokenBalanceAfterBorrow,
                    amount
                );
            }
        }
```
Here let's say lending contract sends 1 wei less than  debtTokenAmountToBorrow due to rounding.Then observedDiffBorrow=10e18-1, so the checks will pass.But the contract balance of debtToken = 10e18-1 as lending contract sends only 10e18-1( assume tokenBalanceBeforeBorrow =0).
now if we observe _depositToPoolImplementation function returns (debtTokenAmountToBorrow = 10e18).
https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/blob/bef3b2af8c38552a9e697ff8eecfd9bdf3982834/contracts/vaults/dloop/core/DLoopCoreBase.sol#L780
```solidity
        return debtTokenAmountToBorrow;
```
now let's see further flow,
https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/blob/bef3b2af8c38552a9e697ff8eecfd9bdf3982834/contracts/vaults/dloop/core/DLoopCoreBase.sol#L708-L714
```solidity
        uint256 debtAssetBorrowed = _depositToPoolImplementation(
            caller,
            assets
        );


        // Transfer the debt asset to the receiver
        debtToken.safeTransfer(receiver, debtAssetBorrowed);
```
As we can observe here this contract tries to send 10e18 amount of debt tokens to receiver but this contract balance of debt token was 10e18-1.So this transfer call will revert causing DOS of important deposit::DLoopCoreBase function.

**Attack Scenario**\
There are conditions for this attack to work ,
1)debt token balance of DLoopCoreBase contract =0 before the borrow(tokenBalanceBeforeBorrow = 0).
which is very much possible as all borrowed debt tokens will be transfered to reciever and this contract doesn't hold debt tokens .
2) Lending contract sends 1 wei less than debtTokenAmountToBorrow(due to rounding).
**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
