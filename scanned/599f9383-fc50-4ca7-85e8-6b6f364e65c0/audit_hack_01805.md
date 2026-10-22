# [M] Overcomplicated unit conversions

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
There are many instances of unit conversion in the system that are implemented in a confusing way. This could result in mistakes in the conversion and possibly failure in correct accounting. It's been seen in the ecosystem that these type of complicated unit conversions could result in calculation mistake and loss of funds.

#### Examples

Here are a few examples:

* /contracts/Bank.sol#L216-L224
```solidity
    function getBorrowRatePerBlock(address _token) public view returns(uint) {
        if(!globalConfig.tokenInfoRegistry().isSupportedOnCompound(_token))
        // If the token is NOT supported by the third party, borrowing rate = 3% + U * 15%.
            return getCapitalUtilizationRatio(_token).mul(globalConfig.rateCurveSlope()).div(INT_UNIT).add(globalConfig.rateCurveConstant()).div(BLOCKS_PER_YEAR);

        // if the token is suppored in third party, borrowing rate = Compound Supply Rate * 0.4 + Compound Borrow Rate * 0.6
        return (compoundPool[_token].depositRatePerBlock).mul(globalConfig.compoundSupplyRateWeights()).
            add((compoundPool[_token].borrowRatePerBlock).mul(globalConfig.compoundBorrowRateWeights())).div(10); 
    }
```

* /contracts/Bank.sol#L350-L351
```solidity
                compoundPool[_token].depositRatePerBlock = cTokenExchangeRate.mul(UNIT).div(lastCTokenExchangeRate[cToken])
                    .sub(UNIT).div(blockNumber.sub(lastCheckpoint[_token]));
```

* /contracts/Bank.sol#L384-L385
```solidity
        return lastDepositeRateIndex.mul(getBlockNumber().sub(lcp).mul(depositRatePerBlock).add(INT_UNIT)).div(INT_UNIT);

```


#### Recommendation

Simplify the unit conversions in the system. This can be done either by using a function wrapper for units to convert all values to the same unit before including them in any calculation or by better documenting every line of unit conversion

<!-- Supply advice on how to best fix the problem. -->
