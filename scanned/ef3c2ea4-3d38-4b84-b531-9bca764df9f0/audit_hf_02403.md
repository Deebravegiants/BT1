# [C] Necessity of Single-Shot Initialization of VaultStrategy

## Summary
Severity: Critical
Contest weight: 0.5915
Dataset id: 12954
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function initialize(
    address _pool,
    address _vault,
    address _strategist,
    address _rewards,
    address _keeper
) external virtual {
    pool = _pool;
    _initialize(_vault, _strategist, _rewards, _keeper);
}

function _initialize(
    address _vault,
    address _strategist,
    address _rewards,
    address _keeper
) internal {
    vault = IVault(_vault);
    want = IERC20(vault.token());
    want.safeApprove(_vault, uint256(-1)); // Give Vault unlimited access (might save gas)
    strategist = _strategist;
    rewards = _rewards;
    keeper = _keeper;
    // Initialize variables
    minReportDelay = 0;
    maxReportDelay = 86400;
    profitFactor = 100;
    debtThreshold = 0;
    vault.approve(rewards, uint256(-1)); // Allow rewards to be pulled
}
```
Apparently the above logic does not provide the guarantee that the _initialize() function can be called only once. What's more, it allows anyone to call the function! A bad actor could call initialize() and set the vault to his own address, hence transferring all the want tokens from the pool. Since multiple initializations could cause critical risk for the entire protocol, we suggest to ensure that the initialize() routine may only be called once.

## Recommendation
Ensure that the initialize() function could only be called once during the entire lifetime.
