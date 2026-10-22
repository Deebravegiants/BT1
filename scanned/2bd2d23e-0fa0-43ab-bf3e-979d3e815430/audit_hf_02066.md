# [M] Proper Fee Collection in BancorNetwork::_tradeBNT()

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 11724
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the Bancor V3 protocol is in essence a DEX that has the built-in support of swapping one token to another. And the BancorNetwork contract is the entry point for trading users. While reviewing the current logic of trade fee accounting, we notice the current implementation may reduce the trade fee attribution to the liquidity providers. To elaborate, we show below the full implementation of the _tradeBNT() routine. This is a core function that is designed to perform a single hop between BNT and a base token trade by providing either the source or the target amount. However, if we pay attention to the intermediate call to _bntPool.onFeesCollected(), it attempts to notify the BNT pool on collected fees when the target token is BNT. It comes to our attention the collected fees are calculated as tradeAmountsAndFee.tradingFeeAmount - tradeAmountsAndFee.networkFeeAmount (line 1218), which should be tradeAmountsAndFee.tradingFeeAmount! The reason is that the tradeAmountsAndFee.tradingFeeAmount is already reduced with the network fee, i.e., tradeAmountsAndFee.networkFeeAmount. The current implementation may collect less trade fee, which leads to smaller return for liquidity providers.

```solidity
function _tradeBNT(
    bytes32 contextId,
    Token pool,
    bool isSourceBNT,
    TradeParams memory params,
    address trader
) private returns (TradeAmountAndNetworkFee memory) {
    TradeTokens memory tokens = isSourceBNT
        ? TradeTokens({
            sourceToken: Token(address(_bnt)),
            targetToken: pool
        })
        : TradeTokens({
            sourceToken: pool,
            targetToken: Token(address(_bnt))
        });
    TradeAmountAndFee memory tradeAmountsAndFee = params.bySourceAmount
        ? _poolCollection(pool).tradeBySourceAmount(
            contextId,
            tokens.sourceToken,
            tokens.targetToken,
            params.amount,
            params.limit
        )
        : _poolCollection(pool).tradeByTargetAmount(
            contextId,
            tokens.sourceToken,
            tokens.targetToken,
            params.amount,
            params.limit
        );
    // if the target token is BNT, notify the BNT pool on collected fees
    if (!isSourceBNT) {
        _bntPool.onFeesCollected(
            pool,
            tradeAmountsAndFee.tradingFeeAmount - tradeAmountsAndFee.networkFeeAmount,
            true
        );
    }
    TradeAmounts memory tradeAmounts = params.bySourceAmount
        ? TradeAmounts({
            sourceAmount: params.amount,
            targetAmount: tradeAmountsAndFee.amount
        })
        : TradeAmounts({
            sourceAmount: tradeAmountsAndFee.amount,
            targetAmount: params.amount
        });
    emit TokensTraded({
        contextId: contextId,
        pool: pool,
        sourceToken: tokens.sourceToken,
        targetToken: tokens.targetToken,
        sourceAmount: tradeAmounts.sourceAmount,
        targetAmount: tradeAmounts.targetAmount,
        bntAmount: isSourceBNT ? tradeAmounts.sourceAmount : tradeAmounts.targetAmount,
        targetFeeAmount: tradeAmountsAndFee.tradingFeeAmount,
        bntFeeAmount: isSourceBNT ? tradeAmountsAndFee.networkFeeAmount : tradeAmountsAndFee.tradingFeeAmount,
        trader: trader
    });
    return TradeAmountAndNetworkFee({
        amount: tradeAmountsAndFee.amount,
        networkFeeAmount: tradeAmountsAndFee.networkFeeAmount
    });
}
```

## Recommendation
Revise the above logic to properly account for the trade fee collection in the BNT pool.
