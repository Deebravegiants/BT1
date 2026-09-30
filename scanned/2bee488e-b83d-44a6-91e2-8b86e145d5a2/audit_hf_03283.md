# [M] In `MultiRewardStaking.addRewardToken

## Summary
Severity: Medium
Contest weight: 0.4390
Dataset id: 18027
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the way the staking contract records the reward emission rate for each added ERC20 token. The function that accrues rewards multiplies a stored variable called rewardsPerSecond by the elapsed time, but rewardsPerSecond is kept as a raw token amount without any scaling factor that accounts for the token's decimal precision. Because many popular tokens have fewer than the standard 18 decimals – for example WBTC uses eight decimals and EURS uses only two – the smallest non‑zero unit that can be expressed (one token base unit) translates into a reward rate that is far larger than a reasonable per‑second emission. Consequently, when a low‑decimal token is added, the contract is forced to emit rewards that are orders of magnitude higher than intended (e.g., roughly 0.315 WBTC per year or over 300 000 EURS per year). This breaks the economic model of the protocol, can cause the reward pool to be drained rapidly, and may even make the contract appear to give no reward at all if the calculated amount overflows or is rounded to zero in downstream logic. The issue occurs whenever the addRewardToken function is called with a token whose decimal count does not provide enough granularity for the raw rewardsPerSecond value. It affects any user who stakes tokens expecting a modest reward, the protocol operators who rely on predictable reward distribution, and the overall health of the staking system. The problem was discovered during a manual audit by inspecting the _accrueStatic internal function and testing the reward calculation with tokens of varying decimal places. It is subtle because the code itself looks mathematically correct; the flaw only becomes apparent when the token’s precision limits the ability to express a small emission rate. To remediate the issue, the contract should introduce a rate‑decimals multiplier (for example a constant equal to 10**9) that scales rewardsPerSecond, allowing the contract to represent fractional reward rates with higher precision regardless of the token’s native decimals. By applying this multiplier in both the storage of the rate and the accrual calculation, the protocol can maintain accurate accounting, prevent excessive reward payouts, and preserve the intended economic incentives.

## Proof of Concept
As we can see from `_accrueStatic()`, the `rewardsPerSecond` is a raw amount without any multiplier.
    
```solidity
function _accrueStatic(RewardInfo memory rewards) internal view returns (uint256 accrued) {
    uint256 elapsed;
    if (rewards.rewardsEndTimestamp > block.timestamp) {
        elapsed = block.timestamp - rewards.lastUpdatedTimestamp;
    } else if (rewards.rewardsEndTimestamp > rewards.lastUpdatedTimestamp) {
        elapsed = rewards.rewardsEndTimestamp - rewards.lastUpdatedTimestamp;
    }

    accrued = uint256(rewards.rewardsPerSecond * elapsed);
}
```

But 1 wei for 1 second would be too big an amount for some popular tokens like WBTC(8 decimals) and EURS(2 decimals).

For WBTC, it will be 0.31536 WBTC per year (worth about `$7,200`) to meet this requirement, and for EURS, it must be at least 315,360 EURS per year (worth about `$315,000`).

Such amounts might be too big as rewards and the protocol wouldn’t work properly for such tokens.

## Recommendation
Recommend introducing a `RATE_DECIMALS_MULTIPLIER = 10**9(example)` to increase the precision of `rewardsPerSecond` instead of using the raw amount.
