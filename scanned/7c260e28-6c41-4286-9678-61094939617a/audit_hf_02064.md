# [H] Incorrect targetBalance Calculation in Token Swaps

## Summary
Severity: High
Contest weight: 0.7859
Dataset id: 11717
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Bancor V3 protocol is in essence a DEX protocol that has the built-in support of swapping one token to another. And each swap may have the cost of being charged for the swap fee. While reviewing the current logic of fee collection, we notice the current implementation is flawed and should be corrected. To elaborate, we show below the core swap routine (_processTrade()). For simplicity, we examine the swap case when bySourceAmount and isSourceBNT are true and false, respectively. With that, this routine makes use of the _tradeAmountAndFeeBySourceAmount() helper to compute the tradeAmountAndFee, which contains the expected target token amount (in result.targetAmount line 1377) after the conversion. It comes to our attention that this expected target token amount already removes the network fee. In other words, the update to the pool's target balance result.targetBalance (line 1043) does not take into account the network fee.

```solidity
function _processTrade(TradeIntermediateResult memory result) private view {
    TradeAmountAndTradingFee memory tradeAmountAndFee;
    if (result.bySourceAmount)
        tradeAmountAndFee = _tradeAmountAndFeeBySourceAmount(
            result.sourceBalance,
            result.targetBalance,
            result.tradingFeePPM,
            result.sourceAmount
        );
    result.targetAmount = tradeAmountAndFee.amount;
    // ensure that the target amount is above the requested minimum return amount
    if (result.targetAmount < result.limit)
        revert InsufficientTargetAmount();
    else
        tradeAmountAndFee = _tradeAmountAndFeeByTargetAmount(
            result.sourceBalance,
            result.targetBalance,
            result.tradingFeePPM,
            result.targetAmount
        );
    result.sourceAmount = tradeAmountAndFee.amount;
    // ensure that the user has provided enough tokens to make the trade
    if (result.sourceAmount > result.limit)
        revert InsufficientSourceAmount();
    result.tradingFeeAmount = tradeAmountAndFee.tradingFeeAmount;
    // sync the trading and staked balance
    result.sourceBalance += result.sourceAmount;
    result.targetBalance = result.targetAmount;
    if (result.isSourceBNT)
        result.stakedBalance += result.tradingFeeAmount;
    _processNetworkFee(result);
}
```

Moreover, when the subroutine _processNetworkFee() is invoked, the network fee amount is properly saved in result.tradingFeeAmount (line 1426). However, the target token balance needs to further reduce by the network fee. Namely, we need to add the following statement result.targetBalance -= targetNetworkFeeAmount within the if-branch (lines 1425-1430).

```solidity
function _processNetworkFee(TradeIntermediateResult memory result) private view {
    uint32 networkFeePPM = _networkSettings.networkFeePPM();
    if (networkFeePPM == 0)
        return;
    // calculate the target network fee amount and update the trading fee amount accordingly
    uint256 targetNetworkFeeAmount = MathEx.mulDivF(result.tradingFeeAmount, networkFeePPM, PPM_RESOLUTION);
    result.tradingFeeAmount = targetNetworkFeeAmount;
    if (!result.isSourceBNT)
        result.networkFeeAmount = targetNetworkFeeAmount;
    return;
    // trade the network fee (taken from the base token) to BNT
    result.networkFeeAmount = _tradeAmountAndFeeBySourceAmount(
        result.targetBalance,
        result.sourceBalance,
        0,
        targetNetworkFeeAmount
    ).amount;
    // since we have received the network fee in base tokens and have traded them for BNT (so that the network fee
    // is always kept in BNT), we'd need to adapt the trading liquidity and the staked balance accordingly
    result.targetBalance += targetNetworkFeeAmount;
    result.sourceBalance = result.networkFeeAmount;
    result.stakedBalance = targetNetworkFeeAmount;
}
```

In the same vein, this issue is also present during the execution path where isSourceBNT is true. In particular, the current implementation unfortunately deducts the network fee twice from the target token balance.

## Recommendation
Revise the above swap logic to properly take into account the network fee in the target token balance.
