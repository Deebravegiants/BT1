# [M] getExecutionGasLimit() reports a lower gas limit due to gasPerSwap miscalculation

## Summary
Severity: Medium
Contest weight: 0.5940
Dataset id: 9792
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user calls deposit() or withdraw(), these functions internally call: _payExecutionFee --> PerpetualVault::getExecutionGasLimit() --> GmxProxy::getExecutionGasLimit(). The function getExecutionGasLimit() in GmxProxy.sol fetches gasPerSwap correctly as:

```solidity
    uint256 gasPerSwap = dataStore.getUint(SINGLESWAPGAS_LIMIT);
```

but then assumes the swapPath length to be 1 & never bothers to multiply it with the correct swap hops.

Let's have a look at the GMX implementation. We can see here that SINGLESWAPGAS_LIMIT key is returned by the singleSwapGasLimitKey() function.

```solidity
    // @dev key for single swap gas limit
    // @return key for single swap gas limit
    function singleSwapGasLimitKey() internal pure returns (bytes32) {
        return SINGLESWAPGAS_LIMIT;
    }
```

We can also see that a function like estimateExecuteDecreaseOrderGasLimit() (among many others) calculates the gas limit in the following manner:

```solidity
    // @dev the estimated gas limit for decrease orders
    // @param dataStore DataStore
    // @param order the order to estimate the gas limit for
    function estimateExecuteDecreaseOrderGasLimit(DataStore dataStore, Order.Props memory order) internal view returns (uint256) {
        uint256 gasPerSwap = dataStore.getUint(Keys.singleSwapGasLimitKey());
        uint256 swapCount = order.swapPath().length;
        if (order.decreasePositionSwapType() != Order.DecreasePositionSwapType.NoSwap) {
            swapCount += 1;
        }

@--->   return dataStore.getUint(Keys.decreaseOrderGasLimitKey()) + gasPerSwap * swapCount + order.callbackGasLimit();
    }
```

Notice the gasPerSwap * swapCount term in the return statement. The Gamma implementation misses this or assumes that tokens like WBTC or LINK on both Arbitrum and Avalanche chains will be swappable with WETH in one hop, which is not necessarily true and GMX may use an optimized swap path with more than one hops.

When a user calls deposit() or withdraw(), these functions internally call: _payExecutionFee --> PerpetualVault::getExecutionGasLimit() --> GmxProxy::getExecutionGasLimit(). The function getExecutionGasLimit() in GmxProxy.sol fetches gasPerSwap correctly as:

```solidity
    uint256 gasPerSwap = dataStore.getUint(SINGLESWAPGAS_LIMIT);
```

but then assumes the swapPath length to be 1 & never bothers to multiply it with the correct swap hops.

Let's have a look at the GMX implementation. We can see here that SINGLESWAPGAS_LIMIT key is returned by the singleSwapGasLimitKey() function.

```solidity
    // @dev key for single swap gas limit
    // @return key for single swap gas limit
    function singleSwapGasLimitKey() internal pure returns (bytes32) {
        return SINGLESWAPGAS_LIMIT;
    }
```

We can also see that a function like estimateExecuteDecreaseOrderGasLimit() (among many others) calculates the gas limit in the following manner:

```solidity
    // @dev the estimated gas limit for decrease orders
    // @param dataStore DataStore
    // @param order the order to estimate the gas limit for
    function estimateExecuteDecreaseOrderGasLimit(DataStore dataStore, Order.Props memory order) internal view returns (uint256) {
        uint256 gasPerSwap = dataStore.getUint(Keys.singleSwapGasLimitKey());
        uint256 swapCount = order.swapPath().length;
        if (order.decreasePositionSwapType() != Order.DecreasePositionSwapType.NoSwap) {
            swapCount += 1;
        }

@--->   return dataStore.getUint(Keys.decreaseOrderGasLimitKey()) + gasPerSwap * swapCount + order.callbackGasLimit();
    }
```

Notice the gasPerSwap * swapCount term in the return statement. The Gamma implementation misses this or assumes that tokens like WBTC or LINK on both Arbitrum and Avalanche chains will be swappable with WETH in one hop, which is not necessarily true and GMX may use an optimized swap path with more than one hops.

User may end up paying less than required execution fee and the Keepers end up paying additional amount from their own pockets.

As the contest page specifies for Depositors:

Must provide sufficient execution fees for operations

## Recommendation
Either fetch the swapPath hops from GMX and multiply that to gasPerSwap OR increase the buffer on top of the calculated gas limit to stay in the safe zone.
