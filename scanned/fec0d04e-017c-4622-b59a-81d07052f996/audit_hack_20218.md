# [M] 5.3.10 Sameparams.SlippageTolis used in two different swaps

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** BridgeFacet.sol#L299-L304 BridgeFacet.sol#L637
**Description:** The Connext protocol does a cross-chain transfer with the help of the Nomad protocol. In order
to use the Nomad protocol, Connext has to convert the adopted token into the local token. For a cross-chain
transfer, users take up two swaps. Adopted -> Local at the source chainandLocal -> Adopted at the
destination chain.
BridgeFacet.sol#L299-L304

```
function xcall(XCallArgs calldata _args) external payable whenNotPaused nonReentrant returns (bytes32) {
...
// Swap to the local asset from adopted if applicable.
(uint256 bridgedAmt, address bridged) = AssetLogic.swapToLocalAssetIfNeeded(
canonical,
transactingAssetId,
amount,
_args.params.slippageTol
);
...
}
```
BridgeFacet.sol#L637
function _handleExecuteLiquidity(
bytes32 _transferId,
bytes32 _canonicalId,
bool _isFast,
ExecuteArgs calldata _args
) private returns (uint256, address) {
...
// swap out of mad* asset into adopted asset if needed
return AssetLogic.swapFromLocalAssetIfNeeded(_canonicalId, _args.local, toSwap,
,! _args.params.slippageTol);
}

The same slippage tolerance_args.params.slippageTolis used in two swaps. In most cases users cannot set
the correct slippage tolerance to protect two swaps.
Assume the Nomad asset is slightly cheaper in both chains. 1 Nomad asset equals 1.01 adopted asset. An
expected swap would be:1 adopted -> 1.01 Nomad asset -> 1 adopted. The right slippage tolerance should
be set at 1.01 and 0.98 respectively. Users cannot set the correct tolerance with a single parameter. This makes
users vulnerable to MEV searchers. Also, user transfers get stuck during periods of instability.
**Recommendation:** Allow users to set two different slippage tolerance for the two swaps.


**Connext:** Solved in PR 1575.
**Spearbit:** Verified.
