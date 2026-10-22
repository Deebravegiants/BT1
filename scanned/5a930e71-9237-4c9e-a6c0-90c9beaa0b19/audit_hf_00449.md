# [M] WasabiRouter::swapVaultToToken

## Summary
Severity: Medium
Contest weight: 0.4429
Dataset id: 1873
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
No withdraw fee applied when swapping tokens
In 2/3 cases we call _takeWithdrawFee which takes a small fee, sends it to the fee receiver and sends the rest to msg.sender, but when we call _swapInternal it's implied that the swap itself will transfer the swapped tokens to msg.sender, skipping the withdraw fee.
```solidity
function swapVaultToToken(
    uint256 _amount,
    address _tokenIn,
    address _tokenOut,
    bytes calldata _swapCalldata
) external nonReentrant {
    // Withdraw tokenIn from vault on user's behalf
    _withdrawFromVault(_tokenIn, _amount);
    if (_tokenIn != _tokenOut) {
        if (_tokenOut == address(0) && _tokenIn == address(weth)) {
            // Unwrap WETH to ETH
            weth.withdraw(_amount);
            _takeWithdrawFee(_tokenOut, _amount);
        } else {
            // Perform the swap
            _swapInternal(_tokenIn, _amount, _swapCalldata);
        }
    } else {
        // Transfer the withdrawn assets to user (minus withdraw fee)
        _takeWithdrawFee(_tokenOut, _amount);
    }
    // SwapRouter should transfer tokenOut directly to user (and fee receiver)
    if (_tokenOut == address(0)) {
        if (address(this).balance != 0) revert InvalidETHReceived();
    } else if (IERC20(_tokenOut).balanceOf(address(this)) != 0) {
        revert InvalidTokensReceived();
    }
    // If full amount of tokenIn was not used, return it to the vault
    _depositToVault(_tokenIn, IERC20(_tokenIn).balanceOf(address(this)));
}
```
Skipping withdraw fees leading to losses to the protocol

## Recommendation
Rework the logic behind _swapInternal. Maybe the tokenIn and tokenOut of the swap can be arguments of the function and the rest of the calldata is built around them, this way the logic will be flexible enough to support many different tokens, and you'll still be able to have control over the swap itself and from there you can apply the fee where you see fit.
