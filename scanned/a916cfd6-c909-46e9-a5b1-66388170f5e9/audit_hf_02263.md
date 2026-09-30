# [H] Incorrect Price Decimals in LionSwapFeeLP

## Summary
Severity: High
Contest weight: 0.6291
Dataset id: 12413
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LionDEX protocol also comes with a LionSwapFeeLP contract that allows users to purchase vault LP tokens with protocol tokens, i.e., LionToken or esLionToken. The purchase naturally involves the price calculation of related tokens. While examining the current purchase price, we notice an extra decimal adjustment, which should be removed. To elaborate, we show below the related swap() routine. It basically swaps the given protocol tokens (LionToken or esLionToken) to the vault LPs. The required protocol token amount (line 98) is computed as needLion = LPAmount.mul(LPPrice).div(LionPrice).div(1e24), which needs to be revised as needLion = LPAmount.mul(LPPrice).div(LionPrice). In other words, the decimals adjustment of div(1e24) at the end is not necessary. The same issue is also applicable to the getLionAmount() routine.
```solidity
function swap(IERC20 buyToken, uint256 LPAmount, uint256 maxLion) public {
    require(discountLevel[LPAmount] > 0, "LionSwapFeeLP: invalid level");
    require(
        buyToken == LionToken || buyToken == esLionToken,
        "LionSwapFeeLP: buy token invalid"
    );
    uint256 LionPrice = getLionPrice();
    uint256 LPPrice = vault.getMaxPrice(address(LPToken));
    uint256 needLion = LPAmount.mul(LPPrice).div(LionPrice).div(1e24);
    require(needLion <= maxLion, "LionSwapFeeLP: slippage");
    require(
        buyToken.balanceOf(msg.sender) >= needLion,
        "LionSwapFeeLP: Lion balance invalid"
    );
    require(
        buyToken.allowance(msg.sender, address(this)) >= needLion,
        "LionSwapFeeLP: Lion allowance invalid"
    );
    buyToken.safeTransferFrom(msg.sender, address(this), needLion);
    uint256 feeLPAmount = getDiscount(LPAmount);
    feeLP.mintTo(msg.sender, feeLPAmount);
    splitLionOrEsLion(buyToken, needLion);
    emit Swap(msg.sender, buyToken, LPAmount, needLion, feeLPAmount);
}
```

## Recommendation
Revisit the above logic to ensure the right swap price is used for vault LP purchase.
