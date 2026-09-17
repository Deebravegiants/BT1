# [M] 5.3.5 YieldManagercan stake locked funds

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** DSRYieldProvider.sol#L86, LidoYieldProvider.sol#L

**Description:** When L2 bridge withdrawals are finalized in theWithdrawalQueuethe funds are considered locked
as the user can now withdraw these funds from the queue. However, bothYieldProvider'sstakefunctions allow
staking this locked amount.

**Recommendation:** Consider reverting if locked funds are staked:


# DRAFT

```
// DSRYieldProvider
/// @inheritdoc YieldProvider
function stake(uint256 amount) external override onlyDelegateCall {
```
- uint256 daiBalance = DAI.balanceOf(address(YIELD_MANAGER));
+ uint256 daiBalance = YIELD_MANAGER.getTokenBalance();
    if (amount > daiBalance) {
       revert InsufficientStakableFunds();
    }
    if (amount > 0) {
       DSR_MANAGER.join(address(YIELD_MANAGER), amount);
    }
}

```
// LidoYieldProvider
/// @inheritdoc YieldProvider
function stake(uint256 amount) external override onlyDelegateCall {
```
- if (amount > YIELD_MANAGER.lockedValue()) {
+ if (amount > YIELD_MANAGER.getTokenBalance()) {
    revert InsufficientStakableFunds();
}
LIDO.submit{value: amount}(address(0));
}

Additionally, consider renaminglockedValuetototalBalanceandgetTokenBalancetogetAvailableBalanceor
similar names as the current names are ambiguous.
