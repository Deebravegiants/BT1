# [H] Reentrancy in distributePremium allows attacker

## Summary
Severity: High
Contest weight: 0.7865
Dataset id: 22762
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
distributePremium is used when purchasing/renewing/topping up memberships. It
has a mechanism to refund excess ETH sent that is sent for the fee.
The refund process allows the attacker to re-enter into the FairSideNetwork before
updating important variables such as userMembership[primaryAddress] and
totalPWPCSB.
The above variables are updated only after the refund — therefore by re-entering
multiple times, critical limit checks are bypassed.
Check the IMPACT section for more details on the wide range of impacts.
When purchasing/renewing or topping up memberships, a membership fee is paid
BEFORE creation of the membership and before incrementing the totalPWPCSB.
```solidity
function _purchaseMembership(
    address primaryAddress,
    uint256 costShareBenefit,
    address coverAddress,
    TokenType tokenType
) private {
    validateCapitalPool(costShareBenefit);
    // array counts from 0
    if ((userMembership[primaryAddress].length + 1) > maxCoverWallet) {
        revert FSNetwork_MaxMembershipReached();
    }
    distributePremium(coverCostETH, tokenType);
    unchecked {
        membershipCount += 1;
    }
    uint256 coverId = membershipCount;
    Membership storage membershipId = membership[coverId];
    // update storages
    setCoverCounts(costShareBenefit);
    userMembership[primaryAddress].push(coverId);
}

function setCoverCounts(uint256 costShareBenefit) internal {
    totalPWPCSB += costShareBenefit;
}

function distributePremium(uint256 membershipFeeETH, TokenType tokenType)
internal {
    // send back excess ETH
    if (msg.value > membershipFeeETH) {
        payable(msg.sender).sendValue(msg.value - membershipFeeETH);
    }
}
```
Notice that distributePremium is called before setCoverCounts and before
userMembership[primaryAddress].push(coverId).
distributePremium refunds excess ETH to the user.
https://github.com/FairSideNetwork/FairsideContractsV2/blob/main/2/contracts/network/FairSideNetwork.sol#L548
The user can call purchaseMembership again when receiving the refund and before
the above variables are set.
In this state, the total amount of memberships a user has and the total cost share
benefits are not updated so the user can bypass the total amount of membership
check and validateCapitalPool checks regarding totalPWPCSB:
```solidity
function validateCapitalPool(uint256 costShareBenefit) private view {
    if (getFShareRatio() < 1 ether) {
        revert FSNetwork_InsufficientCapitalToCoverMembership();
    }
    if (totalPWPCSB + costShareBenefit > getMaxTotalCostShareBenefits()) {
        revert FSNetwork_ExceedsMaxCostShareBenefitLimit();
    }
}

function getFShareRatio() internal view returns (uint256) {
    // FSHARERatio = Capital Pool / FSHARE (scaled by 1e18)
    uint256 fShareRatio = getCapitalPool().div(getNetworkFshare());
    return fShareRatio;
}

function getNetworkFshare() internal view returns (uint256) {
    return riskBasedCapital + lossRatio.mul(totalPWPCSB.mul(PWPCoverCost));
}
```
Notice that FSHARE and the FSD price are also impacted by not updating
totalPWPCSB:
```solidity
function getFSDPrice() public view override returns (uint256) {
    // FSHARE = Total Available Cost Share Benefits / Gearing Factor
    uint256 fShare = getTokenFShare();
    uint256 capitalPool = getCapitalPool();
    return FairSideFormula2.f(capitalPool, fShare);
}

function getTokenFShare() internal view returns (uint256) {
    uint256 fShare = totalPWPCSB.mul(100) / fsd.gearingFactor();
    return fShare;
}
```
Additionally, this impacts the FSD contract calculation of calculateDeltaOfFSD.
Impacts include:
1. User can bypass the limit to the number of wallets he can cover (2). He can
create as many wallets as desired.
2. The FSHARE% < 100% check is bypassed. This puts the system in an insolvency
risk.
3. The maximum CSB limit is bypassed which can lead to an insolvency risk.
4. The FSD token price will not increase with relation to total CSB (FSHARE). This
means that during the reentrancy a lower amount of FSD tokens are minted.
Less fees can be paid in FSD. The attacker can also take advantage of the
disproportion of the total ETH reserve total CSB calculation in
calculateDeltaOfFSD.

## Recommendation
Either:
1. Revert the TX if msg.value is not exactly membershipFeeETH.
2. Add a reentrancy guard in all purchase, renew and topup functions.
