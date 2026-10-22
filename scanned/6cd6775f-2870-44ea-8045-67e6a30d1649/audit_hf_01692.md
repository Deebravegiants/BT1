# [H] MJR-1 Incorrect calculation of rewardPerLiquidity

## Summary
Severity: High
Contest weight: 0.0215
Dataset id: 9270
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an incorrect calculation of the per‑liquidity reward amount in a staking rewards contract. The contract updates a variable called rewardPerLiquidity based on the elapsed time since the last update, assuming that the elapsed time can be up to the full reward duration. When the first user deposits an NFT after the reward period has already been started by a call to notify(), the expression (lastTimeRewardApplicable() - lastUpdateTime) becomes smaller than the configured DURATION. Because the formula multiplies the reward rate by this time delta, the resulting rewardPerLiquidity value is either zero or far lower than intended. As a consequence the contract does not allocate any reward tokens to the staked liquidity, effectively freezing the tokens that were meant to be distributed as incentives. This situation occurs only under the specific timing condition where the initial deposit happens after the reward period has begun and before any other deposit has updated the accounting state. Users who stake NFTs expect to earn reward tokens proportional to their share of liquidity, but they receive nothing, seeing their reward balance remain at zero while the contract holds undistributed tokens. The issue was discovered during a formal security audit performed by MixBytes, where the auditors traced the reward calculation logic and identified that the time‑difference term can be less than the full duration, breaking the accounting assumptions. The bug is subtle because normal operation—where deposits occur early in the reward period—does not expose the problem, making it easy to miss in testing. It belongs to the class of accounting or reward‑distribution bugs where a formula incorrectly handles edge‑case timing, leading to locked funds and broken incentive economics. To remediate the issue the rewardPerLiquidity computation should be revised to correctly handle cases where the elapsed time is less than the full duration, for example by using the actual elapsed time without assuming it reaches DURATION, or by initializing lastUpdateTime appropriately so that the delta never becomes negative or zero when rewards should be accruing. A proper fix restores the intended reward flow, ensuring that users receive the correct amount of tokens and that no funds remain unintentionally frozen in the contract.

## Recommendation
We recommend to change the calculation of rewardPerLiquidity.
