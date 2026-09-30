# [M] Revisited Logic of Market::_logTrade()

## Summary
Severity: Medium
Contest weight: 0.4594
Dataset id: 13148
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Symmetry protocol, the Market contract is one of the main entries for user interactions. In particular, one entry routine, i.e., trade(), is designed to open/close a LONG/SHORT position. While examining its logic, we notice a common internal _logTrade() routine needs to be improved. To elaborate, we show below the related code snippet of the Market contract. By design, the protocol will charge a certain trading fee when opening/closing a LONG/SHORT position. Especially, part of the trading fee will be distributed to the holders of the veABF token. The _logTrade() routine is designed to meet the requirement. Inside the routine, we notice the tokenToUsd() is incorrectly called (line 399) to calculated the baseToken amount used as incentives, which directly undermines the assumption of the protocol design. Given this, we suggest to improve the implementation as below: uint amountToDistribute = usdToToken(baseToken, int(_fee), false).multiplyDecimal(IMarketSettings(settings).getIntVals(VESYM_FEE_INCENTIVE_RATIO)).toUint256() (line 399).

```solidity
function trade(address _account, address _token, int _sizeDelta, int _price) external onlyOperator returns (int) {
    IPerpTracker perpTracker_ = IPerpTracker(perpTracker);
    require(perpTracker_.latestUpdated(_token) == block.timestamp, "Market: fee is not updated");
    (int execPrice, uint tradingFee, uint couponUsed) = IFeeTracker(feeTracker).discountedTradingFee(_account, _sizeDelta, _price, true);
    (int marginDelta, int oldSize, int newSize) = perpTracker_.settleTradeForUser(_account, _token, _sizeDelta, execPrice);
    _modifyMargin(_account, usdToToken(baseToken, marginDelta, false));
    liquidityBalance = usdToToken(baseToken, perpTracker_.settleTradeForLp(_token, -_sizeDelta, execPrice, oldSize, newSize), false);
    _logTrade(_account, _sizeDelta.multiplyDecimal(_price).abs().toUint256(), tradingFee - couponUsed);
    emit Traded(_account, _token, _sizeDelta, _price, tradingFee, couponUsed);
    return execPrice;
}

function _logTrade(address _account, uint _volume, uint _fee) internal {
    // veSYM incentives
    uint amountToDistribute = tokenToUsd(baseToken, int(_fee), false).multiplyDecimal(IMarketSettings(settings).getIntVals(VESYM_FEE_INCENTIVE_RATIO)).toUint256();
    _transferLiquidityOut(feeTracker, amountToDistribute);
    IFeeTracker(feeTracker).distributeIncentives(amountToDistribute);
    // Volume
    VolumeTracker(volumeTracker).logTrade(_account, _volume);
}
```

## Recommendation
Improve the implementation of the _logTrade() routine as above-mentioned.
