# [M] Lack of array length validation in DODORouteProxy.sol#dodoMultiswap.

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L384-L443
Type: audit-issue

## Details
# Lack of array length validation in DODORouteProxy.sol#dodoMultiswap.

## Summary

Lack of array length validation in dodoMultiswap.

## Vulnerability Detail

When calling the function mixSwap, we validate the supplied parameter and the array length:

```solidity
   function mixSwap(
        address fromToken,
        address toToken,
        uint256 fromTokenAmount,
        uint256 minReturnAmount,
        address[] memory mixAdapters,
        address[] memory mixPairs,
        address[] memory assetTo,
        uint256 directions,
        bytes[] memory moreInfos,
        bytes memory feeData,
        uint256 deadLine
    ) external payable judgeExpired(deadLine) returns (uint256 receiveAmount) {
        require(mixPairs.length > 0, "DODORouteProxy: PAIRS_EMPTY");
        require(mixPairs.length == mixAdapters.length, "DODORouteProxy: PAIR_ADAPTER_NOT_MATCH");
        require(mixPairs.length == assetTo.length - 1, "DODORouteProxy: PAIR_ASSETTO_NOT_MATCH");
        require(minReturnAmount > 0, "DODORouteProxy: RETURN_AMOUNT_ZERO");
```

However, such array length check is missing in DODORouteProxy.sol#dodoMultiswap.

We have 

```solidity
    function dodoMutliSwap(
        uint256 fromTokenAmount,
        uint256 minReturnAmount,
        uint256[] memory splitNumber,  
        address[] memory midToken,
        address[] memory assetFrom,
        bytes[] memory sequence, 
        bytes memory feeData,
        uint256 deadLine
    ) external payable judgeExpired(deadLine) returns (uint256 receiveAmount) {
```

we call

```solidity
_multiSwap(midToken, splitNumber, sequence, assetFrom);
```

there is no array length validation at all in the functoin _multiswap.

## Impact

The user may pass in improperly length and the transaction fails.

Given this code for _multiswap, for example,

```solidity
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
```

For example, if the user pass in 100 items in splitNumber array but the array AssetFrom has few elements, the assetFrom[i - 1] access would revert in index out of range error.

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L384-L443

## Tool used

Manual Review

## Recommendation

We recommend the project add the array length validation the same as the project did for the function DODORouteProxy.sol#mixSwap
