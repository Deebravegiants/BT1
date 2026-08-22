# [M] Swap functions are Reenterable

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-03-lifinance
Published: 2022-03-29
Source: https://github.com/code-423n4/2022-03-lifinance-findings/issues/109
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-03-lifinance/blob/699c2305fcfb6fe8862b75b26d1d8a2f46a551e6/src/Facets/DiamondCutFacet.sol#L14-L22
https://github.com/code-423n4/2022-03-lifinance/blob/699c2305fcfb6fe8862b75b26d1d8a2f46a551e6/src/Facets/CBridgeFacet.sol#L92-L121
https://github.com/code-423n4/2022-03-lifinance/blob/699c2305fcfb6fe8862b75b26d1d8a2f46a551e6/src/Facets/AnyswapFacet.sol#L74-L110
https://github.com/code-423n4/2022-03-lifinance/blob/699c2305fcfb6fe8862b75b26d1d8a2f46a551e6/src/Facets/NXTPFacet.sol#L85-L102
https://github.com/code-423n4/2022-03-lifinance/blob/699c2305fcfb6fe8862b75b26d1d8a2f46a551e6/src/Facets/NXTPFacet.sol#L150-L171


# Vulnerability details

## Impact

There is a reenterancy vulnerability in functions which call `Swapper._executeSwap()` which would allow the attacker to change their `postSwapBalance`.

The functions following similar logic to that seen in `GenericSwapFacet.swapTokensGeneric()`.

```
        uint256 receivingAssetIdBalance = LibAsset.getOwnBalance(_lifiData.receivingAssetId);

        // Swap
        _executeSwaps(_lifiData, _swapData);

        uint256 postSwapBalance = LibAsset.getOwnBalance(_lifiData.receivingAssetId) - receivingAssetIdBalance;

        LibAsset.transferAsset(_lifiData.receivingAssetId, payable(msg.sender), postSwapBalance);
```

This logic records the balance before and after the `_executeSwaps()` function. The difference is then transferred to the `msg.sender`.

The issue occurs since it is possible for an attacker to reenter this function during `_executeSwaps()`, that is because execute swap makes numerous external calls, such as to the AMM, or to untrusted ERC20 token addresses.

If a function is called such as `WithdrawFacet.withdraw()` this will impact the calculations of `postSwapBalance` which will account for the funds transferred out during withdrawal. Furthermore, any functions which transfers funds into the contract will also be counted in the `postSwapBalance` calculations.

Vulnerable Functions:
- `GenericSwapFacet.swapTokensGeneric()`
- `CBridgeFacet.swapAndStartBridgeTokensViaCBridge()`
- `AnyswapFacet.swapAndStartBridgeTokensViaAnyswap()`

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-03-lifinance-findings/issues/109_
