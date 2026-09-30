# [M] 5.2.3 ReplacecreateRetryableTicketNoRefundAliasRewrite()withdepositEth()

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** ArbitrumBridgeFacet.sol#L90-L
**Description:** The function_startBridge()of theArbitrumBridgeFacetusescreateRetryableTicketNoRefun-
dAliasRewrite(). According to the docs: address-aliasing, this method skips some address rewrite magic that
depositEth()does.
NormallydepositEth()should be used, according to the docs depositing-and-withdrawing-ether.
Also this method will be deprecated after nitro: Inbox.sol#L283-L297.
While the bridge doesn’t do these checks ofdepositEth(), it is easy for developers, that call the LiFi contracts
directly, to make mistakes and loose tokens.
function _startBridge(...) ... {
if (LibAsset.isNativeAsset(_bridgeData.assetId)) {
gatewayRouter.createRetryableTicketNoRefundAliasRewrite{ value: _amount + cost }(...);
} ...
}

**Recommendation:** ReplacecreateRetryableTicketNoRefundAliasRewrite()withdepositEth().
**LiFi:** In principle, retryable tickets can alternatively be used to deposit Ether; this could be preferable to the special
eth-deposit message type if, e.g., more flexibility for the destination address is needed, or if one wants to trigger
the fallback function on the L2 side. Reverted with PR #79.
**Spearbit:** Verified.
