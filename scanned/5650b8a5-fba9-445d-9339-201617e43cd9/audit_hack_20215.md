# [M] 5.3.3 _handleExecuteLiquiditydoesn’t consistently check forreceiveLocalOverrides

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** BridgeFacet.sol#L571-L638
**Description:** The function_handleExecuteLiquidity()initially checks forreceiveLocalbut does not check for
receiveLocalOverrides. Later on it does check for both of values.
function _handleExecuteLiquidity(... ) ... {
...
if (
!_args.params.receiveLocal &&// doesn't check for receiveLocalOverrides
s.routerBalances[_args.routers[0]][_args.local] < toSwap &&
s.aavePool != address(0)
) {
...
if (_args.params.receiveLocal || s.receiveLocalOverrides[_transferId]) {// extra check
return (toSwap, _args.local);
}
}


As a result, the portal may pay the bridge user in the adopted asset when they opted to override this behaviour
to avoid slippage conditions outside of their boundaries, potentially leading to an unwarranted reception of funds
denominated in the adopted asset.
**Recommendation:** Consider adding a check forreceiveLocalOverridesto the Aave portal eligibility check.
**Connext:** Solved in PR 1644.
**Spearbit:** Verified.
