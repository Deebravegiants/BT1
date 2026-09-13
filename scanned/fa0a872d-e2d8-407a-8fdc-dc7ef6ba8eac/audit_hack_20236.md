# [M] 5.2.6 ArbitrumBridgeFacetdoes not check ifmsg.valueis enough to cover the cost

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** ArbitrumBridgeFacet.sol#L97-L
**Description:** TheArbitrumBridgeFacetdoes not check whether the users’ provided ether (msg.value) is enough
to cover_amount + cost. If there are remaining ethers in LiFi’s LibDiamond address, exploiters can set a large
cost and sweep the ether.
function _startBridge(
...
) private {
...
uint256 cost = _bridgeData.maxSubmissionCost + _bridgeData.maxGas * _bridgeData.maxGasPrice;
if (LibAsset.isNativeAsset(_bridgeData.assetId)) {
gatewayRouter.createRetryableTicketNoRefundAliasRewrite{ value: _amount + cost }(
...
);
} else {
gatewayRouter.outboundTransfer{ value: cost }(
...
);
}

**Recommendation:** Always check the inbound ether is enough to cover the outbound ether. There are different
possible cases.

- startBridgeTokensViaArbitrumBridgeandassetId != NATIVE_ASSET.
    **-** checkmsg.value > cost


- startBridgeTokensViaArbitrumBridgeandassetId == NATIVE_ASSET.
    **-** checkmsg.value > cost + amount
- swapAndStartBridgeTokensViaArbitrumBridgeandassetId != NATIVE_ASSET
    **-** calculatesreceived _ether = post_swap_ether - pre_swap_etherand checksreceived _ether >
       cost
- swapAndStartBridgeTokensViaArbitrumBridgeandassetId == NATIVE_ASSET
    **-** calculatesreceived _ether = post_swap_ether - pre_swap_etherand checksreceived _ether >
       amount + cost
**LiFi:** Fixed with PR #104.
**Spearbit:** Verified.
