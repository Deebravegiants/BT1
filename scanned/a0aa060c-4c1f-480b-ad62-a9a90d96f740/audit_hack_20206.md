# [H] 5.2.10ExecutorandAssetLogicdeals with the native tokens inconsistently that breaksexecute()

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** Executor.sol#L142 AssetLogic.sol#L127-L151, BridgeFacet.sol#L644-L
**Description:** When dealing with an external callee theBridgeFacetwill transfer liquidity to theExecutorbefore
callingExecutor.execute.
In order to send the native token:

- TheExecutorchecks for_args.assetId == address(0).
- AssetLogic.transferAssetFromContract()disallowsaddress(0).
Note: also see issueExecutorreverts on receiving native tokens fromBridgeFacet.


```
contract BridgeFacet is BaseConnextFacet {
function _handleExecuteTransaction() ...{
...
AssetLogic.transferAssetFromContract(_asset, address(s.executor), _amount);// _asset may not
,! be 0
(bool success, bytes memory returnData) = s.executor.execute(
IExecutor.ExecutorArgs(
...
_asset, // assetId parameter from ExecutorArgs // must be 0 for Native asset
...
)
);
...
}
}
library AssetLogic {
function transferAssetFromContract( address _assetId, ... ) {
...
// No native assets should ever be stored on this contract
if (_assetId == address(0)) revert AssetLogic__transferAssetFromContract_notNative();
if (_assetId == address(s.wrapper)) {
// If dealing with wrapped assets, make sure they are properly unwrapped
// before sending from contract
s.wrapper.withdraw(_amount);
Address.sendValue(payable(_to), _amount);
}
}
}
contract Executor is IExecutor {
function execute(ExecutorArgs memory _args) external payable override onlyConnext returns (bool,
,! bytes memory) {
...
bool isNative = _args.assetId == address(0);
...
}
}
```
TheBridgeFacetcannot handle external callees when using native tokens.
**Recommendation:** The native tokens are either represented asaddress(0)oraddress(wrapper)throughout the
whole code base, causing this inconsistency to be error prone. Recommend the team to go through the whole
code base and make sure it’s used consistently.
**Connext:** Solved in PR 1532.
**Spearbit:** Verified.
**Connext:** Alternate approach: removed native asset handling. Implemented in PR 1641.
**Spearbit:** Verified.
