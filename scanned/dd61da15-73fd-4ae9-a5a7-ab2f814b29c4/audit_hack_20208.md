# [H] 5.2.12SponsorVaultsponsors full transfer amount inreimburseLiquidityFees().

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** BridgeFacet.sol#L660-L
**Description:** TheBridgeFacetpassesargs.amountas_liquidityFeewhen callingreimburseLiquidityFees.
Instead of sponsoringliquidityFee, the sponsor vault would sponsor full transfer amount to the reciever.
Note: Luckily the amount inreimburseLiquidityFeesis capped byrelayerFeeCap.
function _handleExecuteTransaction(...) ... {
...
(bool success, bytes memory data) = address(s.sponsorVault).call(
abi.encodeWithSelector(s.sponsorVault.reimburseLiquidityFees.selector, _asset, _args.amount,
,! _args.params.to)
);
}


**Recommendation:** Passargs.amount * (s.LIQUIDITY_FEE_DENOMINATOR - s.LIQUIDITY_FEE_NUMERATOR)
/ s.LIQUIDITY_FEE_DENOMINATORinstead.
**Connext:** Solved in PR 1551.
**Spearbit:** Verified.
