# [M] The modifier `onlyExistingRoute` works incorrectly

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1298
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/helpers/SwapHandler/GenericSwapAndBridgeHandler.sol#L29-L32


# Vulnerability details

## Impact

The modifier [onlyExistingRoute]() checks incorrectly.
This modifier is reverted if `routes[_routeId].route == address(0)` and `routes[_routeId].isEnabled == false`.
Thus, this modifier can be passed if `routes[_routeId].route != address(0)` or `routes[_routeId].isEnabled == true`

## Proof of Concept

The modifier `onlyExistingRoute` is reverted if `routes[_routeId].route == address(0)` and `routes[_routeId].isEnabled == false`.

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/helpers/SwapHandler/GenericSwapAndBridgeHandler.sol#L29-L32

```Solodity
File: contracts\helpers\SwapHandler\GenericSwapAndBridgeHandler.sol
29:     modifier onlyExistingRoute(uint256 _routeId) {
30:         if (routes[_routeId].route == address(0) && !routes[_routeId].isEnabled) revert RouteNotFound();
31:         _;
32:     }
```

But, this modifier must be reverted only if `routes[_routeId].route == address(0)` or `routes[_routeId].isEnabled == false`

## Tools Used

Manual Review

## Recommended Mitigation Steps

It is recommended to change the code as follows:

```diff
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1298_
