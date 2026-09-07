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

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/128_
