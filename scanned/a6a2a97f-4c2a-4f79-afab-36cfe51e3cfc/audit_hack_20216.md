# [M] 5.3.6 Not alwayssafeApprove(..., 0)

## Summary
Severity: Medium
Source: https://github.com/aave/aave-v3-periphery/blob/ca184e5278bcbc1c
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** NomadFacet.sol#L176-L242, AssetLogic.sol#L308-L362, PortalFacet.sol#L179-L197,
AssetLogic.sol#L263-L295, Executor.sol#L142-L339
**Description:** Some functions like_reconcileProcessPortalofBaseConnextFacetand_swapAssetOutofAs-
setLogicdosafeApprove(..., 0)first.
contract NomadFacet is BaseConnextFacet {
function _reconcileProcessPortal( ... ) ... {
...
// Edge case with some tokens: Example USDT in ETH Mainnet, after the backUnbacked call there
,! could be a remaining allowance if not the whole amount is pulled by aave.
// Later, if we try to increase the allowance it will fail. USDT demands if allowance is not 0,
,! it has to be set to 0 first.
// Example:
[ParaSwapRepayAdapter.sol#L138-L140](https://github.com/aave/aave-v3-periphery/blob/ca184e5278bcbc1c
0d28c3dbbc604041d7cfac50b/contracts/adapters/paraswap/ParaSwapRepayAdapter.sol#L138-L140)

```
,!
,!
SafeERC20.safeApprove(IERC20(adopted), s.aavePool, 0);
SafeERC20.safeIncreaseAllowance(IERC20(adopted), s.aavePool, totalRepayAmount);
...
}
}
```
While the following functions don’t do this:

- xcallofBridgeFacet.
- _backLoanofPortalFacet.
- _swapAssetofAssetLogic.
- executeofExecutor.
This could result in problems with tokens likeUSDT.


```
contract BridgeFacet is BaseConnextFacet {
function xcall(XCallArgs calldata _args) external payable nonReentrant whenNotPaused returns
,! (bytes32) {
SafeERC20.safeIncreaseAllowance(IERC20(bridged), address(s.bridgeRouter), bridgedAmt);
}
}
contract PortalFacet is BaseConnextFacet {
function _backLoan(...) ... {
SafeERC20Upgradeable.safeIncreaseAllowance(IERC20Upgradeable(_asset), s.aavePool, _backing +
,! _fee);
}
}
library AssetLogic {
function _swapAsset(...) ... {
SafeERC20.safeIncreaseAllowance(IERC20(_assetIn), address(pool), _amount);
}
}
contract Executor is IExecutor {
function execute( ... ) ... {
SafeERC20.safeIncreaseAllowance(IERC20(_args.assetId), _args.to, _args.amount);
}
}
```
**Recommendation:** Consider addingsafeApprove(..., 0).
**Connext:** Solved in PR 1550.
**Spearbit:** Verified.
