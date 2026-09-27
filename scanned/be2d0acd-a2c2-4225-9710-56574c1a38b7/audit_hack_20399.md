# [M] 5.3.2 Claimable gauge distributions are locked whenkillGaugeis called

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** Voter.sol#L297-L
**Description:** When a gauge is killed, theclaimable[_gauge]key value is cleared. Because any rewards received
by theVotercontract are indexed and distributed in proportion to each pool's weight, this claimable amount is
permanently locked within the contract.
**Recommendation:** Consider returning theclaimableamount to theMintercontract. It is important to note that
votes will continue to persist on the killed gauge, so it may also make sense to wipe these votes too. Otherwise,
the killed gauge will continue to accrue rewards from theMintercontract.
**Velodrome:** We intend on returning claimable to Minter. I think clearing votes is not possible without a lot of
changes to the code as there is no way of fetching which nfts voted for a specific pool without iterating through
all of them and this may have unexpected side effects withreset, so I think the best that can be done is to
communicate that the gauge has been killed.
**Velodrome:** Fixed in commit e4b230.
**Spearbit:** The fix will send a gauge's claimable funds back to theMintercontract inkillGauge(). However, it
does not handle the case where residual votes on a pool will continue to allocate minted tokens to a gauge.
**Velodrome:** Is it possible for the mitigation to be complete by returning funds inupdateFor(address _gauge)as
well? By complete I mean addressing the edge case that votes remain on the pool, and thus causing minting
supply to be trapped.
That way, even if there are residual votes (_supplied), anyclaimablethat exists is returned to the minter instead
of being trapped inVoter. Note thatupdateForis only callable once per week as theindexvalue is only updated
once per week whenupdate_periodis called.
Something like this:
if (_delta > 0) {
uint256 _share = (uint256(_supplied) * _delta) / 1e18;// add accrued difference for each supplied
,! token
if (isAlive[_gauge]) {
claimable[_gauge] += _share;
} else {
IERC20(rewardToken).safeTransfer(minter, _share);
}
}

**Spearbit:** Agreed that the residual votes issue would be remediated ifupdateFor()was updated to transfer back
minted tokens if the gauge has been killed.
