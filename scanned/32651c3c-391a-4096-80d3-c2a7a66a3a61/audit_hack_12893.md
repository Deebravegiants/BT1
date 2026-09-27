# [M] The calculation of `twap` in `Univ3Twap.getTwap` could overflow

## Summary
Severity: Medium
Reporter: GimelSec
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L74
Type: audit-issue

## Details
# The calculation of `twap` in `Univ3Twap.getTwap` could overflow

## Summary

`Univ3Twap.getTwap` calculates the `twap` by multiplying all the individual twaps of the pools and then dividing it by 10**decimals. However, it's important to be aware that an overflow could occur when performing the multiplication of the twaps.

## Vulnerability Detail

`Univ3Twap.getTwap` calculates the `twap` by multiplying all the individual twaps of the pools and then dividing it by 10**decimals.
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L74
```solidity
    function getTwap(address[] calldata path, uint24[] calldata fees, uint32 twapLength) public view returns(uint256) {
        …

        uint256 twap = 1;
        uint256 decimals = 0;

        for(uint i = 0; i < path.length-1; i++) {
            uint256 t = getSingleHopTwap(path[i], path[i+1], fees[i], twapLength);
            twap = twap * t; // @audit: overflow could occur.
            decimals += IERC20(path[i+1]).decimals();
        }

        return twap * 10**IERC20(path[path.length-1]).decimals() / 10**decimals;
    }
```

## Impact

`Univ3Twap.getTwap` may suffer from overflow. 

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L74

## Tool used

Manual Review

## Recommendation

Modify the implementation to mitigate overflow:
```diff
    function getTwap(address[] calldata path, uint24[] calldata fees, uint32 twapLength) public view returns(uint256) {
        …

        uint256 twap = 1;
-       uint256 decimals = 0;
+       uint256 prevDecimals = 1;

        for(uint i = 0; i < path.length-1; i++) {
            uint256 t = getSingleHopTwap(path[i], path[i+1], fees[i], twapLength);
-           twap = twap * t;
+           twap = twap * t / prevDecimals;
-           decimals += IERC20(path[i+1]).decimals();
        }

-       return twap * 10**IERC20(path[path.length-1]).decimals() / 10**decimals;
+       return twap;
    }

```
