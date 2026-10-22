# [M] Sandwiched Advance With Inﬂuenced Reward/Debt Allocation

## Summary
Severity: Medium
Contest weight: 0.5934
Dataset id: 13375
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.2, the VSD protocol implements a unique expansion and contraction mechanism in order to meet the target collateral ratio (even the prices of underlying collateral assets can be volatile) and maximize the benefits of active participants including bonded liquidity providers and value set share (VSS) holders. Whether an epoch undergoes expansion and contraction is determined by current market price measured from specified pools (via Oracle). To elaborate, we show below the step() routine from Regulator. This routine measures and determines current VSD price, and grows/shrinks the total supply if the price is above/below the specified upper/below threshold.

```solidity
function step() internal {
    Decimal.D256 memory price = oracleCapture();
    uint256 allReserve = _updateReserve();
    if (price.greaterThan(Decimal.D256({ value: getSupplyIncreasePriceThreshold() })))
        growSupply(price, allReserve);
        return;
    if (price.lessThan(Decimal.D256({ value: getSupplyDecreasePriceThreshold() })))
        shrinkSupply(price, allReserve);
        return;
    emit SupplyNeutral(epoch());
}
```

Speciﬁcally, if we focus on the expansion-handling logic, the helper routine growSupply() mints additional VSD tokens and sells them on specified UniswapV2 pairs (e.g., USDC/VSD, DAI/VSD, and USDT/VSD).

```solidity
function growSupply(Decimal.D256 memory price, uint256 allReserve) private {
    uint256 lessDebt = resetDebt(Decimal.zero());
    (uint256 sellAmount, uint256 returnAmount) = _getSellAndReturnAmount(
        price.value,
        getSupplyIncreasePriceTarget(),
        allReserve
    );
    _sellAndDepositCollateral(sellAmount, allReserve);
    uint256 mintAmount = returnAmount.mul(10000).div(getCollateralRatio());
    (uint256 newRedeemable, uint256 newSupply, uint256 newReward) = increaseSupply(
        mintAmount.sub(sellAmount)
    );
    emit SupplyIncrease(epoch(), price.value, sellAmount, newRedeemable, lessDebt, newSupply, newReward);
}
```

We notice the sell-oﬀ of minted VSD tokens is performed by sending the tokens to UniswapV2 in order to swap one token to another. And the swap operation does not specify any restriction on possible slippage and is therefore vulnerable to possible front-running attacks, resulting in a smaller return of collateral. Fortunately, this step() is restricted in a way that only EOA account is qualiﬁed to invoke, which signiﬁcantly reduces the risks from possible ﬂashloans. However, it should be emphasized that this does not eliminate this risk as powerful miners may still be able to launch sandwich-related attacks. A similar issue also exists in the vote() routine for proposing a new candidate with manipulated bondedVotes (by inﬂuencing the balanceOfBondedDollar() outcome). Note that this is a common issue plaguing current AMM-based DEX solutions. Speciﬁcally, a large trade may be sandwiched by a preceding sell to reduce the market price, and a tailgating buy-back of the same amount plus the trade amount. Such sandwiching behavior unfortunately causes a loss and brings a smaller return as expected to the trading user. As a mitigation, we may consider specifying the restriction on possible slippage caused by the trade or referencing the TWAP or time-weighted average price of UniswapV2. Nevertheless, we need to acknowledge that this is largely inherent to current blockchain infrastructure and there is still a need to continue the search eﬀorts for an eﬀective defense. Depending on the expansion/contraction, this issue may have implication to inﬂuence reward allocation and coupon allowance. The very same issue is also possible to bypass the proposal qualiﬁcation restriction in governance.

## Recommendation
Develop an eﬀective mitigation to the above sandwich attack to better protect the interests of farming users.
