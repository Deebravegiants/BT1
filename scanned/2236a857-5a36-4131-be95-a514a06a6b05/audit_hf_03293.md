# [H] The `collect` function transfers zero fees due to incorrect execution order

## Summary
Severity: High
Contest weight: 0.9072
Dataset id: 18099
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Detailed description of the impact of this finding. The `collect()` function will always transfer ZERO fees. At the same time, non-zero `_feesPosition` will be burned.

```
_feesPositions[id][msg.sender].burn(long0Fees, long1Fees, shortFees);
```

As a result, the contracts will be left in an inconsistent state. The user will burn `_feesPositions` without receiving the fees!

## Proof of Concept
Provide direct links to all referenced code in GitHub. Add screenshots, logs, or any other relevant proof that illustrates the concept.

The `collect()` function will always transfer ZERO fees in the following line:

```solidity
// transfer the fees amount to the recipient
ITimeswapV2Pool(poolPair).transferFees(param.strike, param.maturity, param.to, long0Fees, long1Fees, shortFees);
```

This is because, at this moment, the values of `long0Fees`, `long1Fees`, `shortFees` have not been calculated yet, actually, they will be equal to zero. Therefore, no fees will be transferred. The values of `long0Fees`, `long1Fees`, `shortFees` are calculated afterwards by the following line:

```solidity
(long0Fees, long1Fees, shortFees) = _feesPositions[id][msg.sender].getFees(param.long0FeesDesired, param.long1FeesDesired, param.shortFeesDesired);
```

Therefore, `ITimeswapV2Pool(poolPair).transferFees` must be called after this line to be correct.

## Recommendation
We moved the line `ITimeswapV2Pool(poolPair).transferFees` after `long0Fees`, `long1Fees`, `shortFees` have been calculated first.

```solidity
function collect(TimeswapV2LiquidityTokenCollectParam calldata param) external returns (uint256 long0Fees, uint256 long1Fees, uint256 shortFees, bytes memory data) {
    ParamLibrary.check(param);

    bytes32 key = TimeswapV2LiquidityTokenPosition({token0: param.token0, token1: param.token1, strike: param.strike, maturity: param.maturity}).toKey();

    // start the reentrancy guard
    raiseGuard(key);

    (, address poolPair) = PoolFactoryLibrary.getWithCheck(optionFactory, poolFactory, param.token0, param.token1);

    uint256 id = _timeswapV2LiquidityTokenPositionIds[key];

    _updateFeesPositions(msg.sender, address(0), id);

    (long0Fees, long1Fees, shortFees) = _feesPositions[id][msg.sender].getFees(param.long0FeesDesired, param.long1FeesDesired, param.shortFeesDesired);

    if (param.data.length != 0)
        data = ITimeswapV2LiquidityTokenCollectCallback(msg.sender).timeswapV2LiquidityTokenCollectCallback(
            TimeswapV2LiquidityTokenCollectCallbackParam({
                token0: param.token0,
                token1: param.token1,
                strike: param.strike,
                maturity: param.maturity,
                long0Fees: long0Fees,
                long1Fees: long1Fees,
                shortFees: shortFees,
                data: param.data
            })
        );

    // transfer the fees amount to the recipient
    ITimeswapV2Pool(poolPair).transferFees(param.strike, param.maturity, param.to, long0Fees, long1Fees, shortFees);

    // burn the desired fees from the fees position
    _feesPositions[id][msg.sender].burn(long0Fees, long1Fees, shortFees);

    if (long0Fees != 0 || long1Fees != 0 || shortFees != 0) _removeTokenEnumeration(msg.sender, address(0), id, 0);

    // stop the reentrancy guard
    lowerGuard(key);
}
```

> Fixed in [PR](https://github.com/Timeswap-Labs/Timeswap-V2-Monorepo/pull/256).
