# [H] Wrong calculation in the cover cost during membership top-up

## Summary
Severity: High
Contest weight: 0.8985
Dataset id: 22761
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users get undercharged when topping up membership due to faulty calculation of
the cover cost.
When a user is topping up their membership, a prorated cost for the additional
cover is calculated based on the remaining days.
This is done in the function FairSideNetwork.sol::calculateCoverCost
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
The problem is that dailycost is calculated in seconds while daysRemaining is
calculated in days.
This discrepancy results in the rate being much lower and the user is undercharged
when topping up membership.
• Let's take a user who purchases 50 ETH of protection. They will get charged
0.0195 * 50e18 = 975000000000000000 for a full year
• If halfway through the year, they want to top up another 50 ETH, they should
be charged approximately half what it would cost for 1 year
• Instead, due to the faulty calculation, they will be charged much less as can be
seen in the POC below:
```solidity
import { assert, expect } from "chai";
import { ethers } from "hardhat";
import { ethToWei, weiToEth, toUnits, toWholeUnits, increaseTime,
createRandomWalletAddress, getEthBalance } from "../helpers/base";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
import { FSD, FairSideNetwork } from "../../typechain-types";
import { FSDPhase } from "../Interfaces/enums";
import fsdContractsDeployer from "../helpers/test.deployer";

describe("FaultyTopup", () => {
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
        // Increase wait time by half a year.
        await increaseTime(182.5 * 86400);
        const proratedCost = (await
        fairSideNetwork.connect(tom).estimateCost(ethToWei("50"),
        membership.duration)) as any;

        console.log("50 ETH for 182.5 days:", proratedCost);
        await expect(fairSideNetwork.connect(tom).topupMembership(coverId,
        ethToWei("50"), { value: ethToWei("1.5") })).not.be.reverted;
    });
});
```
• Place the POC in a file called faultyTopup.test.ts in the test/network folder
and run it:
npx hardhat test ./test/network/faultyTopup.test.ts
FaultyTopup
50 ETH for 365 days: BigNumber { value: "975000000000000000" }
50 ETH for 182.5 days: BigNumber { value: "5626902581300" }
Now if we fix the issue by modifying the calculation in
FairSideNetwork.sol::calculateCoverCost
```solidity
function calculateCoverCost(uint256 costShareBenefit, uint256 duration)
internal view returns (uint256) {
    uint256 coverCost = getCoverCost();
    uint256 fee = costShareBenefit.mul(coverCost);
    if (block.timestamp > duration) {
        return fee;
    } else {
        uint256 dailycost = (coverCost * 86400) / MEMBERSHIP_DURATION;
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
Then rerun the POC, we get:
50 ETH for 365 days: BigNumber { value: "975000000000000000" }
50 ETH for 182.5 days: BigNumber { value: "486164383561638600" }
This is now accurate and 50 ETH for half a year is approximately half what it would
be for 1 year.
Loss of funds for the protocol and other users/stakers as premium top ups are
undercharged.

## Recommendation
Fix the issue by modifying the calculation in
FairSideNetwork.sol::calculateCoverCost
```solidity
function calculateCoverCost(uint256 costShareBenefit, uint256 duration)
internal view returns (uint256) {
    uint256 coverCost = getCoverCost();
    uint256 fee = costShareBenefit.mul(coverCost);
    if (block.timestamp > duration) {
        return fee;
    } else {
        uint256 dailycost = (coverCost * 86400) / MEMBERSHIP_DURATION;
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
