# [H] 5.1.1 swapInternal()shouldn't usemsg.sender

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:**

- BridgeFacet.sol#L337-L
- BridgeFacet.sol#L659-L
- AssetLogic.sol#L150-L
- AssetLogic.sol#L229-L
- SwapUtils.sol#L798-L
**Description:** As reported by the Connext team, the internal stable swap checks ifmsg.senderhas sufficient funds
onexecute(). Thismsg.senderis therelayerwhich normally wouldn't have these funds so the swaps would fail.
The local funds should come from the Connext diamond itself.
BridgeFacet.sol
function execute(ExecuteArgs calldata _args) external nonReentrant whenNotPaused returns (bytes32) {
...
(uint256 amountOut, address asset, address local) = _handleExecuteLiquidity(...);
...
}
function _handleExecuteLiquidity(...) ... {
...
(uint256 amount, address adopted) = AssetLogic.swapFromLocalAssetIfNeeded(...);
...
}

AssetLogic.sol

```
function swapFromLocalAssetIfNeeded(...) ... {
...
return _swapAsset(...);
}
function _swapAsset(... ) ... {
...
SwapUtils.Swap storage ipool = s.swapStorages[_key];
if (ipool.exists()) {
// Swap via the internal pool.
return ... ipool.swapInternal(...) ...
}
}
```
SwapUtils.sol
function swapInternal(...) ... {
IERC20 tokenFrom = self.pooledTokens[tokenIndexFrom];
require(dx <= tokenFrom.balanceOf(msg.sender), "more than you own"); // msg.sender is the relayer
...
}

**Recommendation:** Don't use the balance ofmsg.sender.
**Connext:** Solved in PR 2120.
**Spearbit:** Verified.
