# [M] Lack of curPoolInfo.weight validation in DODORouteProxy.sol#DodoMultiswap

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/28
Type: sherlock-finding

## Details
ctf_sec

medium

# Lack of curPoolInfo.weight validation in DODORouteProxy.sol#DodoMultiswap

## Summary

Lack of curPoolInfo.weight validation in DodoMultiswap

## Vulnerability Detail

We set the total Weight in DODORouteProxy.sol#DodoMultiswap

```solidity
// in PoolInfo, pool weight has 8 bit, so totalWeight < 2**8
uint256 public totalWeight = 100;
```

this parameter is used inside the function DodoMultipswap, which calls _multiswap.

```solidity
uint256 curTotalWeight = totalWeight;
```

and

```solidity
uint256 curTotalAmount = IERC20(midToken[i]).tokenBalanceOf(assetFrom[i - 1]);
uint256 curTotalWeight = totalWeight;

// split amount into all pools if needed, transverse all pool in this split
for (uint256 j = splitNumber[i - 1]; j < splitNumber[i]; j++) {
    PoolInfo memory curPoolInfo;
    {
        (address pool, address adapter, uint256 mixPara, bytes memory moreInfo) = abi
            .decode(swapSequence[j], (address, address, uint256, bytes));

        curPoolInfo.direction = mixPara >> 17;
        curPoolInfo.weight = (0xffff & mixPara) >> 9;
        curPoolInfo.poolEdition = (0xff & mixPara);
        curPoolInfo.pool = pool;
        curPoolInfo.adapter = adapter;
        curPoolInfo.moreInfo = moreInfo;
    }

    // assetFrom[i - 1] is routeProxy when there are more than one pools in this split
    if (assetFrom[i - 1] == address(this)) {
        uint256 curAmount = curTotalAmount * curPoolInfo.weight / curTotalWeight;

        if (curPoolInfo.poolEdition == 1) {
            //For using transferFrom pool (like dodoV1, Curve), pool call transferFrom function to get tokens from adapter
            IERC20(midToken[i]).transfer(curPoolInfo.adapter, curAmount);
        } else {
            //For using transfer pool (like dodoV2), pool determine swapAmount through balanceOf(Token) - reserve
            IERC20(midToken[i]).transfer(curPoolInfo.pool, curAmount);
        }
    }
```

note the line

```solidity
curPoolInfo.weight = (0xffff & mixPara) >> 9;
```

and

```solidity
uint256 curAmount = curTotalAmount * curPoolInfo.weight / curTotalWeight;
```

the mixPara is purely user supplied, 

the value (0xffff & mixPara) >> 9, which is curPoolInfo.weight, can even larger than curTotalWeight.

For example, if the mixPara is 9999999999999999, (0xffff & mixPara) >> 9 is 127, which is larger than the total Weight 100.

Also, the (0xffff & mixPara) >> 9 could also be 0,

Either the curPoolInfo.weight is larger than curTotalWeight or curPoolInfo.weight is 0, the code below would not be working. We cannot transfer more than the current amount to the pool, transferring 0 amoutn to the pool cannot facilitate the swap.

```solidity
uint256 curAmount = curTotalAmount * curPoolInfo.weight / curTotalWeight;
```

## Impact

The swap later after the asset distribution can revert.

```solidity
if (curPoolInfo.direction == 0) {
    IDODOAdapter(curPoolInfo.adapter).sellBase(
        assetFrom[i],
        curPoolInfo.pool,
        curPoolInfo.moreInfo
    );
} else {
    IDODOAdapter(curPoolInfo.adapter).sellQuote(
        assetFrom[i],
        curPoolInfo.pool,
        curPoolInfo.moreInfo
    );
}
```

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L384-L443

## Tool used

Manual Review

## Recommendation

We recommend the project validate all the curPoolInfo.weight sum add up to the total Weight, no curPoolInfo.weight (0xffff & mixPara) >> 9) can be 0 or over total weight.

Also according to the comment: 

```solidity
// in PoolInfo, pool weight has 8 bit, so totalWeight < 2**8
```

We can change from 0xffff & mixPara) >> 9 to 0xffff & mixPara) >> 8 or 0xffff & mixPara) >> smaller number.
