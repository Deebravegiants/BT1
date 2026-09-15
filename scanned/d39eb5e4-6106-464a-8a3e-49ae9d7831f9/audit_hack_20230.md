# [H] 5.1.1 Hardcode bridge addresses viaimmutable

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** OmniBridgeFacet.sol#L34-L106, AxelarFacet.sol#L18-L
**Description:** Most bridge facets call bridge contracts where the bridge address has been supplied as a parameter.
This is inherently unsafe because any address could be called. Luckily, the called function signature is hardcoded,
which reduces risk. However, it is still possible to call an unexpected function due to the potential collisions of
function signatures. Users might be tricked into signing a transaction for the LiFi protocol that calls unexpected
contracts.
One exception is theAxelarFacetwhich sets the bridge addresses ininitAxelar(), however this is relatively
expensive as it requires anSLOADto retrieve the bridge addresses.
Note: also see "Facets approve arbitrary addresses for ERC20 tokens".
function startBridgeTokensViaOmniBridge(..., BridgeData calldata _bridgeData) ... {
...
_startBridge(_lifiData, _bridgeData, _bridgeData.amount, false);
}
function _startBridge(..., BridgeData calldata _bridgeData, ...) ... {
IOmniBridge bridge = IOmniBridge(_bridgeData.bridge);
if (LibAsset.isNativeAsset(_bridgeData.assetId)) {
bridge.wrapAndRelayTokens{ ... }(...);
} else {
...
bridge.relayTokens(...);
}
...
}
contract AxelarFacet {
function initAxelar(address _gateway, address _gasReceiver) external {
...
s.gateway = IAxelarGateway(_gateway);
s.gasReceiver = IAxelarGasService(_gasReceiver);
}
function executeCallViaAxelar(...) ... {
...
s.gasReceiver.payNativeGasForContractCall{ ... }(...);
s.gateway.callContract(destinationChain, destinationAddress, payload);
}
}

**Recommendation:** Set bridge addresses in aconstructorand store them asimmutablevariables. The gas
costs are low and this approach also works withdelegatecalland thus the Diamond pattern.
Note: The Hop bridge protocol has a separate bridge contract for each token, so will require more complicated
code, like a mapping fromsendingAssetIdtobridgeaddress. See hopt.ts.
Note: The Omni bride facet calls the functionsrelayTokens()andwrapAndRelayTokens()which are implemented
in different contracts. So this requires some additional code, see: WETHOmnibridgeRouter.sol#L50, WETHOm-
nibridgeRouter, bridge
Note: this suggestion is also relevant for other addresses that are used, like the WETH address in AccrossFacet,
see AcrossFacet.sol#L
**LiFi:** Fixed with PR #105 and PR #79.


**Spearbit:** Verified.
