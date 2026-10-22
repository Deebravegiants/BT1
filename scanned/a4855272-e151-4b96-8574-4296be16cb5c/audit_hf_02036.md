# [M] Non-initialization of pid in BaseStrategy::constructor()

## Summary
Severity: Medium
Contest weight: 0.4119
Dataset id: 11617
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ApeRocket protocol provide users a number of yield optimization strategies. To facilitate the strategy construction and management, the protocol provides a base strategy template, i.e., BaseStrategy. This BaseStrategy is inherited by all strategy instances.  
To elaborate, we show below its constructor() function. While it properly configures a number of parameters and states, it fails to properly initialize the pid state. Note this pid is used in other routines. For example, the shutdownStrategy() is used to turn off this strategy by retrieving all funds back to the vault. As a result, an uninitialized pid may cause undesirable consequence when the strategy needs to shut down.
```solidity
constructor(
    address _vault,
    address _feeManager,
    address _rewards_contract,
    uint16 _pid
) internal {
    require(_vault != address(0));
    require(_rewards_contract != address(0));
    vault = _vault;
    rewards_contract = _rewards_contract;
    feeManager = _feeManager;
    IERC20(WBNB).safeApprove(_feeManager, uint256(-1));
    keeper = msg.sender;
}
```

## Recommendation
Properly initialize the pool id pid when the strategy is being configured.
