# [M] Division precision loss in createD

## Summary
Severity: Medium
Contest weight: 0.6863
Dataset id: 1754
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The createDistribution function in the contract contains a potential vulnerability
related to precision loss during division calculations, which could lead to incorrect
distribution of rewards. This occurs because the distribution logic divides _amount by
The createDistribution function calculates amountPerEpoch by dividing realAmountToDistribute by the number of epochs. In cases where _amount is large, this division may lead
to precision loss because Solidity's integer division discards the fractional component,
potentially causing small discrepancies in each epoch's reward distribution. These
inaccuracies accumulate over multiple epochs, leading to an overall loss in reward
accuracy. The vulnerability is found in this segment of the createDistribution function:
rder/contracts/GammaRewarder.sol#L108-L147
```solidity
function createDistribution(
    address _hypervisor,
    address _rewardToken,
    uint256 _amount,
    uint64 _startBlockNum,
    uint64 _endBlockNum
) external nonReentrant {
    // Other requirements and checks
    uint256 fee = _amount * protocolFee / BASE_9;
    uint256 realAmountToDistribute = _amount - fee;
    uint256 amountPerEpoch = realAmountToDistribute / ((_endBlockNum - _startBlockNum) / blocksPerEpoch);
    // Further processing
}
```
In this code, amountPerEpoch is calculated by dividing realAmountToDistribute by the
number of epochs (which is derived from block range). The result may have a fractional
part, but Solidity’s integer division will truncate it, leading to precision loss.
Internal pre-conditions
External pre-conditions
Attack Path
While this vulnerability does not entirely prevent the function’s operation, it introduces
inaccuracies in reward distribution that may lead to small amounts being unrewarded
over time. This could be noticeable with large distributions or over long durations, where
cumulative precision loss can result in rewards lower than anticipated.

## Proof of Concept
A Hardhat test can demonstrate the impact of precision loss, especially with large
distributions where each division results in a truncated value. Setup:
1. Deploy a mock ERC20 token (MockRewardToken) and mint tokens to msg.sender.
2. Deploy the distribution contract.
3. Set large values for _amount and a reasonable range for epochs to see the effect of
precision loss.
Create distribution and validate results: Call createDistribution and observe amountPerEpoch to confirm whether the amount lost to precision affects each epoch's accuracy.
```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");
describe("Division Precision Loss in `createDistribution`", function () {
    let rewardToken, distributionContract, owner, addr1;
    const largeAmount = ethers.utils.parseUnits("1000000000", 18); // Large amount for distribution
    const protocolFee = 100; // Simulated fee of 0.01%
    before(async function () {
        [owner, addr1] = await ethers.getSigners();
        // Deploy mock ERC20 reward token
        const MockRewardToken = await ethers.getContractFactory("MockRewardToken");
        rewardToken = await MockRewardToken.deploy("Reward Token", "RTK", 18);
        await rewardToken.deployed();
        // Mint tokens to addr1 for testing
        await rewardToken.mint(addr1.address, largeAmount);
        // Deploy the distribution contract
        const DistributionContract = await ethers.getContractFactory("DistributionContract");
        distributionContract = await DistributionContract.deploy(protocolFee);
        await distributionContract.deployed();
    });
    it("Should exhibit precision loss in `amountPerEpoch` calculation", async function () {
        // Set allowance
        await rewardToken.connect(addr1).approve(distributionContract.address, largeAmount);
        // Calculate expected values manually for comparison
        const epochs = 10; // Example block range divided into 10 epochs
        const realAmountToDistribute = largeAmount.mul(9999).div(10000); // Deduct protocol fee
        const expectedPerEpoch = realAmountToDistribute.div(epochs);
        // Execute createDistribution
        await distributionContract.connect(addr1).createDistribution(
            addr1.address,
            rewardToken.address,
            largeAmount,
            1000,
            2000
        );
        // Fetch distribution info and validate precision loss
        const distribution = await distributionContract.getDistribution(addr1.address);
        expect(distribution.amountPerEpoch).to.be.lt(expectedPerEpoch);
    });
});
```
Running this Hardhat test produces output showing that amountPerEpoch is lower than
expected due to precision loss.

## Recommendation
To mitigate this issue, consider modifying the calculation to use a higher precision
mechanism, such as scaling the division before converting it back. For example, consider
using a 10**18 multiplier to help retain more precision during the division, or calculate amountPerEpoch in a way that evenly distributes any rounding discrepancies over epochs.
```solidity
uint256 amountPerEpoch = realAmountToDistribute * 10**18 / numberOfEpochs; // Multiplied to retain precision
amountPerEpoch = amountPerEpoch / 10**18; // Convert back after scaling
```
Alternatively, use a mod function to calculate any remainder and distribute it across
epochs to ensure accurate distribution.
