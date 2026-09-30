# [M] 5.3.5 Compromised or malicious owner can drain theVotingEscrowcontract ofVELOtokens

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** VotingEscrow.sol#L119-L122, FactoryRegistry.sol#L72-L82
**Description:** TheFactoryRegistrycontract is anOwnablecontract with the ability to control the return value of
themanagedRewardsFactory()function. As such, whenevercreateManagedLockFor()is called inVotingEscrow,
theFactoryRegistrycontract queries themanagedRewardsFactory()function and subsequently callscreateRe-
wards()on this address.
If ownership of theFactoryRegistrycontract is compromised or malicious, thecreateRewards()external call can
return any arbitrary_lockedManagedRewardaddress which is then given an infinite token approval. As a result,
it's possible for all lockedVELOtokens to be drained and hence, this poses a significant centralization risk to the
protocol.
**Recommendation:** Avoid using infinite approvals unless the target is guaranteed to be deterministic and im-
mutable. Consider modifying theincreaseAmount()and all other instances whereIReward(_lockedManage-
dReward).notifyRewardAmount()is called.
The proposed fix may look like the following:
function createManagedLockFor(address _to) external nonReentrant returns (uint256 _mTokenId) {
...
(address _lockedManagedReward, address _freeManagedReward) = IManagedRewardsFactory(
IFactoryRegistry(factoryRegistry).managedRewardsFactory()
).createRewards(voter);

- IERC20(token).approve(_lockedManagedReward, type(uint256).max);
    ...
}
function increaseAmount(uint256 _tokenId, uint256 _value) external nonReentrant {
...
if (_escrowType == EscrowType.MANAGED) {
// increaseAmount called on managed tokens are treated as locked rewards
address _lockedManagedReward = managedToLocked[_tokenId];
+ IERC20(token).approve(_lockedManagedReward, _value);
    IReward(_lockedManagedReward).notifyRewardAmount(address(token), _value);
}
}

**Velodrome:** Fixed in commit 6726f2.
**Spearbit:** Verified.
