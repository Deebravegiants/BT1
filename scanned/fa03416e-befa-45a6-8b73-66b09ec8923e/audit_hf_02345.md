# [H] Potential Reentrancy Risk in closePositionWithId()

## Summary
Severity: High
Contest weight: 0.6361
Dataset id: 12729
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle. This principle is effective in mitigating a serious attack vector known as re-entrancy. Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Specifically, it first calls a function in the vulnerable contract, but before the first instance of the function call is finished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [14] exploit, and the recent Uniswap/Lendf.Me hack [13]. We notice there are several occasions the checks-effects-interactions principle is violated. Using the PikaPerpV2 as an example, the closePositionWithId() function (see the code snippet below) is provided to externally call a token contract to transfer assets. However, the invocation of an external contract requires extra care in avoiding the above re-entrancy. Apparently, the interaction with the external contract (line 437) starts before effecting the update on internal states (e.g., lines 453-457), hence violating the principle. In this particular case, if the external contract has certain hidden logic that may be capable of launching re-entrancy via the very same closePositionWithId() function.

```solidity
// Closes position from Position with id = positionId
function closePositionWithId(
    uint256 positionId,
    uint256 margin
) public {
    // Check params
    require(margin >= minMargin, "!margin");
    // Check position
    Position storage position = positions[positionId];
    require(msg.sender == position.owner, "!owner");
    // Check product
    Product storage product = products[uint256(position.productId)];
    bool isFullClose;
    if (margin >= uint256(position.margin)) {
        margin = uint256(position.margin);
        isFullClose = true;
    }
    uint256 maxExposure = uint256(vault.balance).mul(uint256(product.weight)).mul(exposureMultiplier).div(uint256(totalWeight)).div(10**4);
    uint256 price = _calculatePrice(
        product.feed,
        !position.isLong,
        product.openInterestLong,
        product.openInterestShort,
        maxExposure,
        uint256(product.reserve),
        margin * position.leverage / 10**8
    );
    bool isLiquidatable;
    int256 pnl = _getPnl(position, margin, price);
    if (pnl < 0 && uint256(-1 * pnl) >= margin.mul(uint256(product.liquidationThreshold)).div(10**4)) {
        margin = uint256(position.margin);
        pnl = -1 * int256(uint256(position.margin));
        isLiquidatable = true;
    } else {
        // front running protection: if oracle price up change is smaller than threshold and minProfitTime has not passed, the pnl is be set to 0
        if (pnl > 0 && !_canTakeProfit(position, IOracle(oracle).getPrice(product.feed), product.minPriceChange)) {
            pnl = 0;
        }
    }
    uint256 totalFee = _updateVaultAndGetFee(pnl, position, margin, uint256(product.fee), uint256(product.interest));
    _updateOpenInterest(uint256(position.productId), margin.mul(uint256(position.leverage)).div(BASE), position.isLong, false);
    emit ClosePosition(
        positionId,
        position.owner,
        uint256(position.productId),
        price,
        uint256(position.price),
        margin,
        uint256(position.leverage),
        totalFee,
        pnl,
        isLiquidatable
    );
    if (isFullClose) {
        delete positions[positionId];
    } else {
        position.margin -= uint64(margin);
    }
}
```

## Recommendation
Apply necessary reentrancy prevention by making use of the common nonReentrant modifier.
