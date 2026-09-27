# [H] 5.2.15 Anyone can repay theportalDebtwith different tokens

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** PortalFacet.sol#L80-L113 PortalFacet.sol#L115-L167
**Description:** Routers can provide liquidity in the protocol to improve the UX of cross-chain transfers. Liquidity
is sent to users under the router’s consent before the cross-chain message is settled on the optimistic message
protocol, i.e., Nomad. The router can also borrow liquidity fromAAVEif the router does not have enough of it. It is
the router’s responsibility to repay the debt to AAVE.
contract PortalFacet is BaseConnextFacet {
function repayAavePortalFor(
address _adopted,
uint256 _backingAmount,
uint256 _feeAmount,
bytes32 _transferId
) external payable {
address adopted = _adopted == address(0)? address(s.wrapper) : _adopted;
// Transfer funds to the contract
uint256 total = _backingAmount + _feeAmount;
if (total == 0) revert PortalFacet__repayAavePortalFor_zeroAmount();
(, uint256 amount) = AssetLogic.handleIncomingAsset(_adopted, total, 0);
// repay the loan
_backLoan(adopted, _backingAmount, _feeAmount, _transferId);
}
}

ThePortalFacetdoes not check whether_adoptedis the correct token in debt. Assume that the protocol borrows
ETHfor the current_transferId, thereforeRoutershould repayETHto clear the debt. However, theRoutercan
provide any valid tokens, e.g.DAI,USDC, to clear the debt. This results in the insolvency of the protocol.
Note: a similar issue is also present inrepayAavePortal().
**Recommendation:** Check_adoptedis the correct token in this transfer.
**Connext:** Solved in PR 1559.
**Spearbit:** Verified.
