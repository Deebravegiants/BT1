# [M] rebalanceLite should provide a slippage pro-tection

## Summary
Severity: Medium
Contest weight: 0.5934
Dataset id: 19800
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can lose funds while rebalancing.
The protocol provides two kinds of rebalancing functions - rebalance() and rebalanceLite(). While the function rebalance() is protected from an unintended slippage because the caller can specify amountOutMinimum, rebalanceLite() does not have this protection. This makes the user vulnerable to unintended slippage due to various scenarios.
```solidity
function rebalanceLite(
    uint256 amount,
    int8 polarity,
    uint160 sqrtPriceLimitX96,
    address account
) external nonReentrant returns (uint256, uint256) {
    if (polarity == -1) {
        return _rebalanceNegativePnlLite(amount, sqrtPriceLimitX96, account);
    } else if (polarity == 1) {
        // disable rebalancing positive PnL
        revert PositivePnlRebalanceDisabled(msg.sender);
        // return _rebalancePositivePnlLite(amount, sqrtPriceLimitX96, account);
    } else {
        revert InvalidRebalance(polarity);
    }
}

function _rebalanceNegativePnlLite(
    uint256 amount,
    uint160 sqrtPriceLimitX96,
    address account
) private returns (uint256, uint256) {
    uint256 normalizedAmount = amount.fromDecimalToDecimal(
        ERC20(quoteToken).decimals(),
    );

    _checkNegativePnl(normalizedAmount);
    IERC20(quoteToken).transferFrom(account, address(this), amount);
    IERC20(quoteToken).approve(address(vault), amount);
    vault.deposit(quoteToken, amount);

    bool isShort = false;
    bool amountIsInput = true;

    normalizedAmount,
    isShort,
    amountIsInput,
    sqrtPriceLimitX96
);
    vault.withdraw(assetToken, baseAmount);
    IERC20(assetToken).transfer(account, baseAmount);
}
```
for the Perp's ClearingHouse to fill the position partially when the price limit is here.
```solidity
/// @param sqrtPriceLimitX96 tx will fill until it reaches this price but WON'T REVERT
struct InternalOpenPositionParams {
    address trader;
    address baseToken;
    bool isBaseToQuote;
    bool isExactInput;
    bool isClose;
    uint256 amount;
    uint160 sqrtPriceLimitX96;
}
```
So it is possible that the order is not placed to the full amount. As we can see in the #L626~#L628, the UXD protocol grabs the quote token of amount and deposits to the Perp's vault. And the unused amount will remain in the Perp vault while this is supposed to be returned to the user who called this rebalance function.
Users can lose funds while lite rebalancing.

## Recommendation
Add a protection parameter to the function rebalanceLite() so that the user can specify the minimum out amount.
