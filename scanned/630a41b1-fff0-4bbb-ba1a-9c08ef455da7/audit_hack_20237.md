# [M] 5.2.7 Underpaying Optimisml2gasmay lead to loss of funds

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** OptimismBridgeFacet.sol#L97-L
**Description:** The OptimismBridgeFacet uses Optimism’s bridge with user-provided l2gas.
function _startBridge(
LiFiData calldata _lifiData,
BridgeData calldata _bridgeData,
uint256 _amount,
bool _hasSourceSwap
) private {
...
if (LibAsset.isNativeAsset(_bridgeData.assetId)) {
bridge.depositETHTo{ value: _amount }(_bridgeData.receiver, _bridgeData.l2Gas, "");
} else {
...
bridge.depositERC20To(
_bridgeData.assetId,
_bridgeData.assetIdOnL2,
_bridgeData.receiver,
_amount,
_bridgeData.l2Gas,
""
);
}
}

Optimism’s standard token bridge makes the cross-chain deposit by sending a cross-chain message to L2Bridge.
L1StandardBridge.sol#L114-L


```
// Construct calldata for finalizeDeposit call
bytes memory message = abi.encodeWithSelector(
IL2ERC20Bridge.finalizeDeposit.selector,
address(0),
Lib_PredeployAddresses.OVM_ETH,
_from,
_to,
msg.value,
_data
);
// Send calldata into L
// slither-disable-next-line reentrancy-events
sendCrossDomainMessage(l2TokenBridge, _l2Gas, message);
```
If thel2Gasis underpaid,finalizeDepositwill fail and user funds will be lost.
**Recommendation:** Given the potential risks of losing users’ funds, we recommend to emphasize the risks in the
documents.
**LiFi:** Docs added in PR #78.
**Spearbit:** Verified.
