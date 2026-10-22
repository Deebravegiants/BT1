# [H] Membership top-up on the last day of the duration

## Summary
Severity: High
Contest weight: 0.7866
Dataset id: 22764
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _topupMembership(
    uint256 coverId,
    uint256 costShareBenefit,
    TokenType tokenType
) private {
    validateCapitalPool(costShareBenefit);
    Membership storage membershipId = membership[coverId];
    if (block.timestamp >= membershipId.duration) {
        revert FSNetwork_ExpiredMembershipInGrace();
    }
    uint256 userMembershipCSB = membershipId.availableCostShareBenefits +
    costShareBenefit;
    if (userMembershipCSB > _getMaximumBenefitPerUser()) {
        revert FSNetwork_ExceedsCostShareBenefitLimitPerAccount();
    }
    uint256 coverCostETH = calculateCoverCost(costShareBenefit,
    membershipId.duration);
    distributePremium(coverCostETH, tokenType);
}
```
A user could be charged the full fee for one year instead of a prorated cost for the remaining duration:
```solidity
/**
 * @return cover cost (uint)
 */
function calculateCoverCost(uint256 costShareBenefit, uint256 duration) internal
view returns (uint256) {
    uint256 coverCost = getCoverCost();
    uint256 fee = costShareBenefit.mul(coverCost);
    if (block.timestamp > duration) {
        return fee;
    } else {
        uint256 dailycost = coverCost / MEMBERSHIP_DURATION;
        uint256 daysRemaining = (duration - block.timestamp) / 86400;
        if (daysRemaining == 0) {
            return fee;
        }
        uint256 rate = daysRemaining * dailycost;
        uint256 proratedCostETH = costShareBenefit.mul(rate);
        return (proratedCostETH);
    }
}
```
User being charged the full fee for a year.
```solidity
uint256 daysRemaining = (duration - block.timestamp) / 86400;
if (daysRemaining == 0) {
    return fee;
}
```
POC:
```solidity
import { assert, expect } from "chai";
import { ethers } from "hardhat";
import { ethToWei, weiToEth, toUnits, toWholeUnits, increaseTime,
createRandomWalletAddress, getEthBalance } from "../helpers/base";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
import { FSD, FairSideNetwork } from "../../typechain-types";
import { FSDPhase } from "../Interfaces/enums";
import fsdContractsDeployer from "../helpers/test.deployer";

describe("FinalDayTopup", () => {
    // Accounts
    let owner: SignerWithAddress;
    let random: SignerWithAddress;
    let userAccount3: SignerWithAddress;
    let userAccount1: SignerWithAddress;
    let fsd: FSD;
    let coverID: number;
    let fairSideNetwork: FairSideNetwork;
    let timelockAccount: SignerWithAddress;
    let accounts: any[];
    const coverAddress = "0x41427a1488a16a150959347d05c33e54d4d8467e";

    // purchase membership
    before(async () => {
        accounts = await ethers.getSigners();
        [owner, random, userAccount3, userAccount1] = await ethers.getSigners();
        ({ fsd, fairSideNetwork, timelockAccount } = await
        fsdContractsDeployer(owner));
        const balance = await ethers.provider.getBalance(fsd.address);
    });

    it("should purchase PWP membership cover with ETH ", async () => {
        const [joe, tom] = accounts.slice(17, 19);
        // add funds to capital pool by bonding FSD to curve
        await fsd.connect(joe).bond(1, {
            value: ethToWei("10000"),
        });
        // purchase pwp cover
        const cost = (await
        fairSideNetwork.connect(tom).estimateCost(ethToWei("50"), 0)) as any;
        console.log("50 ETH for 365 days:", cost);
        await fairSideNetwork.connect(tom).purchaseMembership(ethToWei("50"),
        coverAddress, { value: ethToWei("1.5") });
        let coverId = 1;
        let membership = await fairSideNetwork.getMembership(coverId);
        // Increase wait time to the last day of the year.
        await increaseTime(364.5 * 86400);
        const proratedCost = (await
        fairSideNetwork.connect(tom).estimateCost(ethToWei("50"),
        membership.duration)) as any;
        await expect(fairSideNetwork.connect(tom).topupMembership(coverId,
        ethToWei("50"), { value: ethToWei("1.5") })).not.be.reverted;
    });
});
```
npx hardhat test ./test/network/finalDayTopup.test.ts
FinalDayTopup
50 ETH for 365 days: BigNumber { value: "975000000000000000" }
Loss of funds for the user if they top-up their membership on the last day of the
membership duration.

## Recommendation
Either don't allow membership top-up on the last day of the duration or alternatively
use seconds instead of days in calculating the prorated cost.
