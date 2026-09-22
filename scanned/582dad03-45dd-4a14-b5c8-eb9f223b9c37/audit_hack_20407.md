# [M] 5.3.15depositForfunction should be restricted to approved NFT types

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** VotingEscrow.sol#L807
**Description:** ThedepositForfunction was found to accept NFT of all types (normal, locked, managed) without
restriction.
function depositFor(uint256 _tokenId, uint256 _value) external nonReentrant {
LockedBalance memory oldLocked = _locked[_tokenId];
require(_value > 0, "VotingEscrow: zero amount");
require(oldLocked.amount > 0, "VotingEscrow: no existing lock found");
require(oldLocked.end > block.timestamp, "VotingEscrow: cannot add to expired lock, withdraw");
_depositFor(_tokenId, _value, 0, oldLocked, DepositType.DEPOSIT_FOR_TYPE);
}

**Instance 1 - Anyone can call** depositFor **against a locked NFT**
Users should not be allowed to increase the voting power of a locked NFT by calling thedepositForfunction as
locked NFTs are not supposed to vote. Thus, any increase in the voting balance of locked NFTs will not increase
the gauge weight, and as a consequence, the influence and yield of the deposited VELO will be diminished.
In addition, the locked balance will be overwritten when theveNFTis later withdrawn from the managedveNFT,
resulting in a loss of funds.
**Instance 2 - Anyone can call** depositFor **against a managed NFT**
Only theRewardsDistributor.claimfunction should be allowed to calldepositForfunction against a managed
NFT to process rebase rewards claimed and to compound the rewards into theLockedManagedRewardcontract.
However, anyone could also increase the voting power of a managed NFT directly by callingdepositForwith a
tokenIdof a managed NFT, which breaks the invariant.
**Recommendation:** Evaluate the type of NFTs (normal, locked, or managed) that can call thedepositForfunction
within protocol.
Based on the current design of the protocol:

- Normal NFT - Anyone can calldepositForagainst a normal NFT
- Locked NFT - No one should be able to calldepositForagainst a locked NFT
- Managed NFT - OnlyRewardsDistributor.claimfunction is allowed to calldepositForfunction against a
    managed NFT for processing rebase rewards.
Consider implementing the following additional check to disallow anyone from callingdepositForfunction against
a Locked NFT:
function depositFor(uint256 _tokenId, uint256 _value) external nonReentrant {
+ EscrowType _escrowType = escrowType[_tokenId];
+ require(_escrowType != EscrowType.LOCKED, "VotingEscrow: Not allowed to call depositFor against
,! Locked NFT");
LockedBalance memory oldLocked = _locked[_tokenId];
require(_value > 0, "VotingEscrow: zero amount");
require(oldLocked.amount > 0, "VotingEscrow: no existing lock found");
require(oldLocked.end > block.timestamp, "VotingEscrow: cannot add to expired lock, withdraw");
_depositFor(_tokenId, _value, 0, oldLocked, DepositType.DEPOSIT_FOR_TYPE);
}

Sidenote: Additionally, thedepositForfunction should be modified to handle incoming Managed NFT's rebase
rewards from theRewardsDistributor. Refer to the recommendation in"Claimed rebase rewards of managed
NFT are not compounded within LockedManagedReward".


**Velodrome:** Fixed in commit e98472.
**Spearbit:** Verified.
