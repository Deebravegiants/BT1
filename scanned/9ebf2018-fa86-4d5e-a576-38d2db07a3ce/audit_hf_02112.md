# [M] Proper Protocol Fee Accounting in removeMargin()

## Summary
Severity: Medium
Contest weight: 0.4543
Dataset id: 11898
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Deri-V2 protocol is designed to collect necessary protocol fee, which is accumulated in a storage variable _protocolFeeAccrued. The accrued protocol fee is denominated at the BToken0 and will be collected in a number of routines addLiquidity(), removeLiquidity(), trade(), and removeMargin(). However, our analysis of the protocol fee shows the removeMargin() routine has an inconsistent logic in accruing the protocol fee. To elaborate, we show below its implementation.

```solidity
function removeMargin(address owner, uint256 bTokenId, uint256 bAmount, uint256 blength, uint256 slength) public override _router_ _lock_ {
    _updatePricesAndDistributePnl(blength, slength);
    _settleTraderFundingFee(owner, slength);
    _coverTraderDebt(owner, blength);
    IPToken pToken = IPToken(_pTokenAddress);
    BTokenInfo storage b = _bTokens[bTokenId];
    uint256 decimals = b.decimals;
    bAmount = bAmount.reformat(decimals);
    int256 amount = bAmount.utoi();
    int256 margin = pToken.getMargin(owner, bTokenId);
    if (amount >= margin) {
        bAmount = margin.itou();
        _protocolFeeAccrued += margin - margin.reformat(_decimals0);
        // deal with accuracy tail
        margin = 0;
    } else {
        margin -= amount;
        pToken.updateMargin(owner, bTokenId, margin);
    }
    require(_getTraderMarginRatio(owner, blength, slength) >= _minInitialMarginRatio, "insuf t margin");
    IERC20(b.bTokenAddress).safeTransfer(owner, bAmount.rescale(18, decimals));
    emit RemoveMargin(owner, bTokenId, bAmount);
}
```

The inconsistency comes from the margin removal of a non-BToken0 asset. Notice the intended margin for removal may not be the protocol-wide BToken0. However, the protocol fee accrued at line 339 is denominated at the intended margin for removal, hence introducing the inconsistency: `_protocolFeeAccrued += margin - margin.reformat(_decimals0)`.

## Recommendation
Be consistent in calculating the protocol fee in all affected routines.
