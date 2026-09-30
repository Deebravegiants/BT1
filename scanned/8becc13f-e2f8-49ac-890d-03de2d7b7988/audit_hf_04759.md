# [M] withdrawAmount is incorrect when process-

## Summary
Severity: Medium
Contest weight: 0.5939
Dataset id: 22603
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Withdraws from TeahouseLiquidityWarehouse, loop through all teahouse vaults when withdrawing. Withdraw amount will be withdrawn for EVERY liquidity vault instead of only a single one. This will lead to excess withdrawals. Since teahouse vaults withdrawals are subject to withdrawal fees it will cause loss to the vault through excess withdrawal fees.
```solidity
// LiquidityWarehouse.sol#L552-L562
while (missingWithdrawableAmount > 0 && idx < withdrawTargets.length) {
    address withdrawTarget = withdrawTargets[idx];
    if (!s_withdrawTargets.contains(withdrawTarget)) revert InvalidWithdrawTarget(withdrawTarget);
    _withdrawFromTarget(missingWithdrawableAmount, withdrawTarget, data);
    currentAssetBalance = s_terms.asset.balanceOf(address(this));
    missingWithdrawableAmount = currentAssetBalance > withdrawAmount ? 0 : withdrawAmount - currentAssetBalance;
    ++idx;
}
```
```solidity
// _withdrawFromTargets is structured to withdraw one at a time from each target until the full amount has been withdrawn to cover the withdrawal.
// TeahouseLiquidityWarehouse.sol#L37-L54
for (uint256 i; i < s_teahouseVaults.length(); ++i) {
    address teahouseVaultAddr = s_teahouseVaults.at(i);
    bytes[] memory data = new bytes[](2);
    // Calculate number of shares to burn which is the minimum of the amount of shares required to withdraw
    // the withdraw amount and the LP balance of the liquidity warehouse
    uint256 sharesAmt = Math.min(
        _convertToTeahouseShares(teahouseVaultAddr, withdrawAmount),
        IERC20(withdrawTarget).balanceOf(address(this))
    );
    // 1) Action to withdraw
    data[0] = abi.encodeWithSelector(ITeaVaultV3Pair.withdraw.selector, sharesAmt, 0, 0);
    // 2) Action to swap
    data[1] = swapData; // TODO: Can be improved later but this is for illustration purposes
    ITeaVaultV3PairHelper(withdrawTarget).multicall(ITeaVaultV3Pair(teahouseVaultAddr), 0, 0, data);
}
```
TeahouseLiquidityWarehouse is structured in an incompatible way. It attempts to withdraw withdrawAmount from each teahouse vault. Assume 100 USDC is needed to cover a withdraw and there are 3 teahouse vaults. Instead of withdrawing only 100 USDC it will withdraw 300 USDC. https://vault.teahouse.finance/arbitrum/0xB38e48B8Bc33CD65551BdaC8d954801D56625eeC/ Looking at the teahouse vault we can see it has 0.2% withdrawal fee. The excess funds that are withdrawn will need to be deposited again into the vault. This causes the vault to lose funds to this withdrawal fee. Vault will lose funds because of excess withdrawals

## Recommendation
_withdrawFromTarget should be restructured so that it will check the balance of the asset after each withdraw so that it does not withdraw too much.
