# [M] Inaccurate accounting in `TradeImpl::buy` could lead to loss of user funds

## Summary
Severity: Medium
Contest weight: 0.2460
Dataset id: 19119
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Within Dolomite Margin, [`TradeImpl::buy`](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/impl/TradeImpl.sol#L44-L110) is used to perform a buy trade and takes `Actions.BuyArgs memory args` as one of its parameters. Given these arguments are supplied by the caller, they are free to set any arbitrary value for `args.exchangeWrapper`.

This `args.exchangeWrapper` parameter is used to [calculate the amount of `takerWei`](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/lib/Exchange.sol#L106-L111) the contract should receive, and to [calculate how much should actually be transferred](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/lib/Exchange.sol#L138-L145) to the Dolomite contract.

Given it is not guaranteed that these two values will be the same, the issue arises when there is a difference between the amount that should be received versus the actual amount received. This is partially handled in [`TradeImpl::buy`](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/impl/TradeImpl.sol#L84-L89), which ensures the received amount is greater than or equal to the expected amount, acting as a slippage check. However, the internal accounting is [updated](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/impl/TradeImpl.sol#L84-L95) based on the value expected to be received, instead of the value actually received.

Incorrect accounting could result in loss of user funds. Given that it is expected, but not guaranteed, that `takerWei == tokensReceived`, we evaluate the severity to MEDIUM.

## Recommendation
Modify [these lines](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/impl/TradeImpl.sol#L91-L95) to guarantee a correct update to protocol accounting.
```diff
//  TradeImpl::buy
    Require.that(
        tokensReceived.value >= makerWei.value,
        FILE,
        "Buy amount less than promised",
        tokensReceived.value
    );

-   state.setPar(
-       args.account,
-       args.makerMarket,
-       makerPar
-   );
+   state.setParFromDeltaWei(
+       args.account,
+       args.makerMarket,
+       makerIndex,
+       tokensReceived
+   );
```
