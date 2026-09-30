# [H] Long orders always pay lesser in fees while short orders pay more

## Summary
Severity: High
Contest weight: 0.7878
Dataset id: 22911
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
Long orders pay lower fees due to inconsistent margin token price, while short orders incur higher fees. This discrepancy naturally makes long orders more incentivized and short orders more disincentivized.

When a position is opened, there are 3 fees to be charged:
1. closeFee
2. borrowingFee
3. fundingFee

When a LONG position is closed, fees are calculated with the oracle min price:
function updateBorrowingFee(Position.Props storage position, address stakeToken) public {
    position.positionFee.realizedBorrowingFee += realizedBorrowingFeeDelta;
    position.positionFee.realizedBorrowingFeeInUsd += CalUtils.tokenToUsd(
        realizedBorrowingFeeDelta,
        TokenUtils.decimals(position.marginToken),
        OracleProcess.getLatestUsdUintPrice(position.marginToken, position.isLong)
    );
}

function updateFundingFee(Position.Props storage position) public {
    int256 realizedFundingFee;
    if (position.isLong) {
        position.positionFee.realizedFundingFeeInUsd += CalUtils.tokenToUsdInt(
            realizedFundingFeeDelta,
            TokenUtils.decimals(position.marginToken),
            OracleProcess.getLatestUsdPrice(position.marginToken, position.isLong)
        );
    } else {
        realizedFundingFee = CalUtils.usdToTokenInt(
            realizedFundingFeeDelta,
            TokenUtils.decimals(position.marginToken),
            OracleProcess.getLatestUsdPrice(position.marginToken, position.isLong)
        );
        position.positionFee.realizedFundingFeeInUsd += realizedFundingFeeDelta;
    }
}
```

When the positions' `position.positionFee.realizedFundingFeeInUsd` and `position.positionFee.realizedBorrowingFeeInUsd` are updated, these values are used to calculate the total fees in USD and finally used to calculate users and pools' profit/loss.

Assume that the position is fully closed; then these lines will be used to calculate the `settledMargin` and `recordPnlToken`:
```solidity
cache.settledMargin = CalUtils.usdToTokenInt(
    cache.position.initialMarginInUsd.toInt256() - _getPosFee(cache) + pnlInUsd,
    TokenUtils.decimals(cache.position.marginToken),
    tokenPrice
);
cache.recordPnlToken = cache.settledMargin - cache.decreaseMargin.toInt256();
```

`_getPosFee(cache)` is the total sum of fees in USD, and since for a LONG order this is calculated via the oracle's min price, this will be the minimum value in USD. Hence, the `settledMargin` will be a higher value and `recordPnlToken` will be a higher value too.

In the end, LONG orders pay lesser borrowing fees to pool and lesser funding fees to shorts. Short orders are the opposite: they pay more fees to longs and higher fees to pool in borrowing fees.

Textual PoC:  
Assume a tokenA LONG position is being closed; tokenA max price is $1 and min price is $0.9 in oracle.  
5 tokens in borrowing fee and 5 tokens in funding fees are accrued. Since it's a long position, the fees will be calculated in USD as 5 * 0.9 = $4.5 instead of 5 * 1 = $5. Total fees to be paid (excluding closeFee) will be $9.

Assume position `initialMarginInUsd` is $100 and `pnlInUsd` is $50.  
Settled margin will be: toToken(100 - 9 + 50) = 141 tokens (LONG positions use the max price as execution price, hence, tokenPrice is the max value).

However, if the same position would be a SHORT position, then the fees would be $5.5 (using max price?) — clarification needed, but original shows higher fees for shorts.

Long orders pay less fees to shorts in funding fees and pay less borrowing fee and closing fee to pool, whereas short orders are the opposite — they pay more fees to all parties. This discrepancy creates a greater advantage for long orders since they pay lesser funding fees and receive higher funding fees. In a scaled system, this advantage will be a greater problem. Hence, I'll label it as high.

## Recommendation
When calculating the fees, always use the higher price to accrue more fees to parties, or use the lesser price for both. The key point is to use the same pricing for both long and shorts to keep them in the same incentive.
