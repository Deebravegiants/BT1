# [H] 5.2.3 Rebase rewards cannot be claimed after aveNFTexpires

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** RewardsDistributor.sol#L271, RewardsDistributor.sol#L
**Description:**
Note: This issue affects both theRewardsDistributor.claimandRewardsDistributor.claimMany
functions
A user will claim their rebase rewards via theRewardsDistributor.claimfunction, which will trigger theVotingE-
scrow.deposit_forfunction.
function claim(uint256 _tokenId) external returns (uint256) {
if (block.timestamp >= timeCursor) _checkpointTotalSupply();
uint256 _lastTokenTime = lastTokenTime;
_lastTokenTime = (_lastTokenTime / WEEK) * WEEK;
uint256 amount = _claim(_tokenId, _lastTokenTime);
if (amount != 0) {
IVotingEscrow(ve).depositFor(_tokenId, amount);
tokenLastBalance -= amount;
}
return amount;
}

Within theVotingEscrow.deposit_forfunction, therequirestatement at line 812 below will verify that the veNFT
performing the claim has not expired yet.
function depositFor(uint256 _tokenId, uint256 _value) external nonReentrant {
LockedBalance memory oldLocked = _locked[_tokenId];
require(_value > 0, "VotingEscrow: zero amount");
require(oldLocked.amount > 0, "VotingEscrow: no existing lock found");
require(oldLocked.end > block.timestamp, "VotingEscrow: cannot add to expired lock, withdraw");
_depositFor(_tokenId, _value, 0, oldLocked, DepositType.DEPOSIT_FOR_TYPE);
}

If a user claims the rebase rewards after their veNFT's lock has expired, theVotingEscrow.depositForfunction
will always revert. As a result, the accumulated rebase rewards will be stuck in theRewardsDistributorcontract
and users will not be able to retrieve them.
**Recommendation:** Consider sending the claimed VELO rewards to the owner of the veNFT if the veNFT's lock
has already expired.


```
function claim(uint256 _tokenId) external returns (uint256) {
if (block.timestamp >= timeCursor) _checkpointTotalSupply();
uint256 _lastTokenTime = lastTokenTime;
_lastTokenTime = (_lastTokenTime / WEEK) * WEEK;
uint256 amount = _claim(_tokenId, _lastTokenTime);
if (amount != 0) {
```
- IVotingEscrow(ve).depositFor(_tokenId, amount);
+ IVotingEscrow.LockedBalance memory _locked = IVotingEscrow(ve).locked(_tokenId)
+ if (_locked.end < block.timestamp) {
+ address _nftOwner = IVotingEscrow(ve).ownerOf(_tokenId);
+ IERC20(token).transfer(_nftOwner, amount);
+ } else {
+ IVotingEscrow(ve).depositFor(_tokenId, amount);
+ }
    tokenLastBalance -= amount;
}
return amount;
}

**Velodrome:** Fixed in commit 8a71a8.
**Spearbit:** Verified.
