# [H] 5.2.23LienToken payeenot reset on transfer

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** LienToken.sol#L303-L313
**Description:** payeeandownerOfare detached in that owners may setpayeeand owner may transfer theLienTo-
kento a new owner.payeedoes not reset on transfer.
Exploit scenario:

- Owner of aLienTokensets themselves aspayee
- Owner ofLienTokensells the lien to a new owner
- New owner does not updatepayee
- Payments go to address set by old owner
**Recommendation:** Reset payee on transfer.
function transferFrom(
address from,
address to,
uint256 id
) public override(ERC721, IERC721) {
LienStorage storage s = _loadLienStorageSlot();
if (s.lienMeta[id].atLiquidation) {
revert InvalidState(InvalidStates.COLLATERAL_AUCTION);
}
+ delete s.lienMeta[id].payee;
+ emit PayeeChanged(id, address(0));
super.transferFrom(from, to, id);
}
