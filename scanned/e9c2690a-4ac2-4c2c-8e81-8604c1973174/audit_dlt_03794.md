# [M] mstpr-brainbot - If stable tokens depeg, short funding fees will not be accounted properly

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-05-elfi-protocol
Published: 2024-06-20
Source: https://github.com/sherlock-audit/2024-05-elfi-protocol-judging/issues/70
Type: sherlock-finding

## Details
mstpr-brainbot

Medium

# If stable tokens depeg, short funding fees will not be accounted properly

## Summary
Funding fees are calculated using a Masterchef-like per token approach. In long orders, the per token calculation uses the token denomination. However, in short orders, it uses the USD value instead of the token value. If the stable token depegs, either temporarily or indefinitely, the funding fees for short positions will not be accounted for correctly.
## Vulnerability Detail
Short funding fee per qty is denominated in USD terms as we can observe in `MarketQueryProcess::getUpdateMarketFundingFeeRate` function as follows:
```solidity
if (cache.totalLongOpenInterest > 0) {
            cache.currentLongFundingFeePerQty = cache.longPayShort
                ? cache.totalFundingFee.div(cache.totalLongOpenInterest)
                : _boundFundingFeePerQty(
                    cache.totalFundingFee.div(cache.totalLongOpenInterest),
                    cache.fundingFeeDurationInSecond
                );
                // USD to token conversion
            -> cache.longFundingFeePerQtyDelta = CalUtils
                .usdToToken(
                    cache.currentLongFundingFeePerQty,
                    TokenUtils.decimals(symbolProps.baseToken),
                    OracleProcess.getLatestUsdUintPrice(symbolProps.baseToken, true)
                )
                .toInt256();
            cache.longFundingFeePerQtyDelta = cache.longPayShort
                ? cache.longFundingFeePerQtyDelta
                : -cache.longFundingFeePerQtyDelta;
        }
        if (cache.totalShortOpenInterest > 0) {
            // does not converts to USD amount to any stable token 
            cache.shortFundingFeePerQtyDelta = cache.longPayShort
                ? -_boundFundingFeePerQty(
                    cache.totalFundingFee.div(cache.totalShortOpenInterest),
                    cache.fundingFeeDurationInSecond
                ).toInt256()
                : (cache.totalFundingFee.div(cache.totalShortOpenInterest)).toInt256();
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2024-05-elfi-protocol-judging/issues/70_
