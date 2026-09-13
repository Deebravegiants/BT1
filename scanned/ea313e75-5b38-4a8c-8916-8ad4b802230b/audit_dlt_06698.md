# [H] DOS of withdraw::DLoopCoreBase function when swapper contract sends more collateral tokens by even just 1 or 2 wei.

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-18
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/128
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** Rajeshkotaru189
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/rudhra1749)

  **Beneficiary:** 0x51060Ecc85024a1F82a47190d769a5849C889b50
  **Submission hash (on-chain):** 0xaeffd3e284fb2fe8a61f50a9f399788caa4ac074bf471cc315085895f3de6eec
  **Severity:** high
  
  **Description:**
  **Description**\
https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/blob/bef3b2af8c38552a9e697ff8eecfd9bdf3982834/contracts/common/SwappableVault.sol#L83-L137
```solidity
    function _swapExactOutput(
        ERC20 inputToken,
        ERC20 outputToken,
        uint256 amountOut,
        uint256 amountInMaximum,
        address receiver,
        uint256 deadline,
        bytes memory extraData
    ) internal returns (uint256) {
        uint256 inputTokenBalanceBefore = inputToken.balanceOf(address(this));
        uint256 outputTokenBalanceBefore = outputToken.balanceOf(address(this));


        // Perform the swap
        uint256 amountIn = _swapExactOutputImplementation(
            inputToken,
            outputToken,
            amountOut,
            amountInMaximum,
            receiver,
            deadline,
            extraData
        );
        uint256 inputTokenBalanceAfter = inputToken.balanceOf(address(this));
        uint256 outputTokenBalanceAfter = outputToken.balanceOf(address(this));


        // Make sure the spent input token amount is not greater than the amount in maximum
        if (inputTokenBalanceAfter < inputTokenBalanceBefore) {
            uint256 spentInputTokenAmount = inputTokenBalanceBefore -
                inputTokenBalanceAfter;
            if (spentInputTokenAmount > amountInMaximum) {
                revert SpentInputTokenAmountGreaterThanAmountInMaximum(
                    spentInputTokenAmount,
                    amountInMaximum
                );
            }
            if (spentInputTokenAmount != amountIn) {
                revert SpentInputTokenAmountNotEqualReturnedAmountIn(
                    spentInputTokenAmount,
                    amountIn
                );
            }
        }
        // Do not need to check the input token balance decreased after the swap
        // as it is not a risk for the caller


        // Make sure the received output token amount is exactly the amount out
        if (outputTokenBalanceAfter > outputTokenBalanceBefore) {
            uint256 receivedOutputTokenAmount = outputTokenBalanceAfter -
                outputTokenBalanceBefore;
            if (receivedOutputTokenAmount != amountOut) {
                revert ReceivedOutputTokenAmountNotEqualAmountOut(
                    receivedOutputTokenAmount,
                    amountOut
                );
            }
```
if we see above lines of code,
1)receivedOutputTokenAmount = amount of collateral tokens DLoopDepositorBase contract get's from the swapper contract after the swap.
2)amountOut =  requiredAdditionalCollateralAmount ( this is the exact amount of collateral tokens  we want from swapper contract).as we can see from below,
https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/blob/bef3b2af8c38552a9e697ff8eecfd9bdf3982834/contracts/vaults/dloop/periphery/DLoopDepositorBase.sol#L402-L410
```solidity
        uint256 debtTokenAmountUsedInSwap = _swapExactOutput(
            debtToken,
            collateralToken,
            requiredAdditionalCollateralAmount, // exact output amount
            type(uint256).max, // no slippage protection
            address(this),
            block.timestamp,
            flashLoanParams.debtTokenToCollateralSwapData
        );
```
so let's see this check below,
https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/blob/bef3b2af8c38552a9e697ff8eecfd9bdf3982834/contracts/common/SwappableVault.sol#L132-L136
```solidity
            if (receivedOutputTokenAmount != amountOut) {
                revert ReceivedOutputTokenAmountNotEqualAmountOut(
                    receivedOutputTokenAmount,
                    amountOut
                );
```
it was not required that receivedOutputTokenAmount is exactly equal to amountOut.And swapper contract may send amount greater than  amountOut, at least by 1 or 2 wei. Then  this call will revert. this is not intended behaviour. If receivedOutputTokenAmount is less than amountOut then it will revert in below lines of code,
https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/blob/bef3b2af8c38552a9e697ff8eecfd9bdf3982834/contracts/odos/OdosSwapUtils.sol#L54-L56
```solidity
        if (actualAmountOut < exactOut) {
            revert InsufficientOutput(exactOut, actualAmountOut);
        }
```
so this causes the function call to revert even if we get sufficient amount of collateral tokens from swapper contract.
This will cause DOS to deposit::DLoopDepositorBase function.

**Attack Scenario**\
when a user calls deposit::DLoopDepositorBase function then it will revert if swapper function sends more collateral tokens to DLoopDepositorBase contract even by 1 or 2 wei this will cause the function to revert when it was not supposed to be revert.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
