# [H] 5.2.11Executorreverts on receiving native tokens fromBridgeFacet

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** Executor.sol BridgeFacet.sol#L696, AssetLogic.sol#L127-L
**Description:** When doing an external call inexecute(), theBridgeFacetprovides liquidity into the Executor
contract before callingExecutor.execute. TheBridgeFacettransfers native token whenaddress(wrapper)is
provided. TheExecutorhowever does not have a fallback/ receive function. Hence, the transaction will revert
when theBridgeFacettries to send the native token to the Executor contract.
function _handleExecuteTransaction(
AssetLogic.transferAssetFromContract(_asset, address(s.executor), _amount);
(bool success, bytes memory returnData) = s.executor.execute(...);
}
function transferAssetFromContract(...) ... {
if (_assetId == address(s.wrapper)) {
// If dealing with wrapped assets, make sure they are properly unwrapped
// before sending from contract
s.wrapper.withdraw(_amount);
Address.sendValue(payable(_to), _amount);
} else {
}
}

**Recommendation:** Recommend to add areceivefunction in theExecutorcontract.
receive() payable external {
require(msg.sender == connext);
}

Or unwrap the native asset and send it along with the call to the executor.
**Connext:** Ether sent along with the call. Solved in PR 1532.
**Spearbit:** Verified.
**Connext:** Alternate approach: removed native asset handling. Implemented in PR 31.
**Spearbit:** Verified.
