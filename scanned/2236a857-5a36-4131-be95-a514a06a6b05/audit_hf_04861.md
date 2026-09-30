# [H] Free CSB and bypass of maximum CSB per wallet

## Summary
Severity: High
Contest weight: 0.7856
Dataset id: 22760
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Opening a cost share request at FairSideClaims automatically deducts the claim
amount from the membership cost share benefits. If the request is denied, the
membership cost share benefits are restored.
A user can take advantage of the above behavior to:
1. Get free CSB
2. Get more cover for a wallet than allowed (100 ether).
When opening a cost share request, setAvailableBenefits is called to decrease:
https://github.com/FairSideNetwork/FairsideContractsV2/blob/main/FairsideContractsV2/contracts/network/FairSideClaims.sol#L274
```solidity
function createCostshareRequest(uint256 requestPayout, uint256 claimAmount,
uint256 _csrType, uint256 coverId) private {
    setAvailableBenefits(claimAmount, msg.sender, coverId, false);
}

function setAvailableBenefits(uint256 requestAmount, address account,
uint256 coverId, bool increase) internal {
    if (increase) {
        fairSideNetwork.increaseOrDecreaseCSB(requestAmount, account,
        coverId, true);
    } else {
        fairSideNetwork.increaseOrDecreaseCSB(requestAmount, account,
        coverId, false);
    }
}
```
fairSideNetwork.increaseOrDecreaseCSB:
https://github.com/FairSideNetwork/FairsideContractsV2/blob/main/2/contracts/network/FairSideNetwork.sol#L709
```solidity
function increaseOrDecreaseCSB(
    uint256 amount,
    address account,
    uint256 coverId,
    bool increase
) external override onlyFairSideClaims {
    if (increase) {
        membershipId.availableCostShareBenefits += amount;
    } else {
        membershipId.availableCostShareBenefits -= amount;
    }
}
```
Similarly, when a claim is denied, the cost share benefits are restored:
```solidity
function seedPWPVerdict(uint256 _claimId, Action action, uint256
_csrTypeCore, bytes calldata reason) external onlyGuardian {
    if (action == Action.DENY_CLAIM) {
        setAvailableBenefits(csr.claimAmount, csr.initiator, csr.coverId,
        true);
    }
}
```
Bypass maximum CSB per wallet:
FairSideNetwork limits a covered wallet to cost share benefit of 100 ether.
```solidity
function _getMaximumBenefitPerUser() internal pure returns (uint256) {
    return 100 ether;
}
```
The limit is checked when purchasing, renewing and topping up memberships:
```solidity
function _topupMembership(
    uint256 coverId,
    uint256 costShareBenefit,
    TokenType tokenType
) private {
    uint256 userMembershipCSB = membershipId.availableCostShareBenefits +
    costShareBenefit;
    if (userMembershipCSB > _getMaximumBenefitPerUser()) {
        revert FSNetwork_ExceedsCostShareBenefitLimitPerAccount();
    }
    membershipId.availableCostShareBenefits = userMembershipCSB;
}
```
Therefore a member can:
1. Purchase 100 ETH cost share benefits
2. Create a cost share request of all cost share benefits (this will deduct them
from the membership)
3. Top up 100 ETH cost share benefits
4. Cost share request is denied — all previous cost share benefits are restored
5. Go to step 2
Free CSB
Cost share requests can be opened even after a membership has expired (60 days
after). Therefore a user can:
1. Purchase a membership for 100 ETH CSB
2. Wait 1 year
3. Open a cost share request for 100 ETH
4. Renew membership with lowest amount (1 ETH)
5. Cost share request denied and 100 ETH is restored to membership
6. Member got a free 100 ETH cover
• Member can get free coverage (loss of funds)
• Member can buy unlimited cost share benefits — in case of approved request,
1 request can drain a large portion of the bonding curve reserve
• Since cost share benefits are virtual and need to be backed by the bonding
curve, owning a large amount of them and opening large requests can prevent
unbonding
• Break a core invariant of the system (limiting memberships to 100 ether /
payment for coverage)

## Recommendation
Consider disabling top-ups and renewals for cover IDs that have open requests
