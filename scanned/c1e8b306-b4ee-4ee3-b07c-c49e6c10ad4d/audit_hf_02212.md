# [M] Wrong Reward Rate in HegicWBTCRewards

## Summary
Severity: Medium
Contest weight: 0.6829
Dataset id: 12228
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Hegic protocol has defined two reward contracts, i.e., HegicETHRewards and HegicWBTCRewards. Both inherit from the base contract of HegicETHRewards which has the following constructor and variables.
```solidity
abstract contract HegicRewards is Ownable {
    using SafeMath for uint;
    using SafeERC20 for IERC20;

    IHegicOptions public immutable hegicOptions;
    IERC20 public immutable hegic;

    mapping(uint => bool) public rewardedOptions;
    mapping(uint => uint) public dailyReward;

    uint internal constant MAX_DAILY_REWARD = 165_000e18;
    uint internal constant REWARD_RATE_ACCURACY = 1e8;
    uint internal immutable MAX_REWARDS_RATE;
    uint internal immutable MIN_REWARDS_RATE;
    uint public rewardsRate;

    constructor(
        IHegicOptions _hegicOptions,
        IERC20 _hegic,
        uint maxRewardsRate,
        uint minRewardsRate
    ) public {
        hegicOptions = _hegicOptions;
        hegic = _hegic;
        MAX_REWARDS_RATE = maxRewardsRate;
        MIN_REWARDS_RATE = minRewardsRate;
        rewardsRate = maxRewardsRate;
    }
}
```
However, when the HegicWBTCRewards contract instantiates HegicRewards, we observe the following instantiation.
```solidity
contract HegicWBTCRewards is HegicRewards
    public
    constructor(
        IHegicOptions _hegicOptions,
        IERC20 _hegic
    ) public
    HegicRewards(
        _hegicOptions,
        _hegic,
        1_000_000e18,
        10e18
    )
```
Apparently, they are assuming the decimal of 18, not 8. The decimal mismatch could result in immediate depletion of available rewards for distribution.

## Recommendation
Correct the above-mentioned decimal mismatch in HegicWBTCRewards. Note that HegicETHRewards is not affected.
```solidity
contract HegicWBTCRewards is HegicRewards
    public
    constructor(
        IHegicOptions _hegicOptions,
        IERC20 _hegic
    ) public
    HegicRewards(
        _hegicOptions,
        _hegic,
        1_000_000e8,
        10e8
    )
```
