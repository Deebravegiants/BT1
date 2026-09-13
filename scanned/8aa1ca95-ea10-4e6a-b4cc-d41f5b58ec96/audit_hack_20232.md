# [H] 5.1.6 Too generic calls inGenericBridgeFacetallow stealing of tokens

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** GenericBridgeFacet.sol#L69-L120, LibSwap.sol#L30-L
**Description:** With the contractGenericBridgeFacet, the functionsswapAndStartBridgeTokensGeneric()(via
LibSwap.swap()) and_startBridge()allow arbitrary functions calls, which allow anyone to calltransferFrom()
and steal tokens from anyone who has given a large allowance to the LiFi protocol.
This has been used to hack LiFi in the past.
The followings risks also are present:

- call the Lifi Diamand itself via functions that don’t havenonReentrant.
- perhaps cancel transfers of other users.
- call functions that are protected by a check onthis, likecompleteBridgeTokensViaStargate.


```
contract GenericBridgeFacet is ILiFi, ReentrancyGuard {
function swapAndStartBridgeTokensGeneric(
LibSwap.swap(_lifiData.transactionId, _swapData[i]);
}
function _startBridge(BridgeData memory _bridgeData) internal {
(bool success, bytes memory res) = _bridgeData.callTo.call{ value: value
,! }(_bridgeData.callData);
}
}
library LibSwap {
function swap(bytes32 transactionId, SwapData calldata _swapData) internal {
(bool success, bytes memory res) = _swapData.callTo.call{ value: nativeValue
,! }(_swapData.callData);
}
}
```
**Recommendation:** Whitelist the external call addresses and function signatures for both the dexes and the
bridges. Note: SwapperV2 already contains whitelist functionality for dexes, but isn’t used from this contract.
Alternatively make sure this code isn’t added to the Lifi Diamond anymore. For example, by removing the code
from the repository and/or adding a warning inside the code itself.
**LiFi:** It has been removed from all contracts deployments since the exploit. We do not plan to enable it again, so
we can remove it from the repository. PR #
**Spearbit:** The issue is solved with deletingGenericBridgeFacetcontract.
