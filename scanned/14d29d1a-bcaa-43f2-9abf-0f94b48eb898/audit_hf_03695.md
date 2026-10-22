# [H] RageTrade senior vault USDC deposits are sub-locked due to underflow in withdrawal

## Summary
Severity: High
Contest weight: 0.6124
Dataset id: 19796
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
RageTrade senior vault requires that it maintains deposits above and beyond the current amount loaned to the junior vault. Currently this is set at 90%, that is the vault must maintain at least 10% more deposits than loans. Currently the junior vault is in high demand and very little can be withdrawn from the senior vault. A situation like this is far from ideal because in the even that there is a strong depeg of UXD a large portion of the collateral could be locked in the vault unable to be withdrawn.
DnGmxSeniorVault.sol
```solidity
function beforeWithdraw(
    uint256 assets,
    uint256,
    address
) internal override {
    /// @dev withdrawal will fail if the utilization goes above maxUtilization value due to a withdrawal
    // totalUsdcBorrowed will reduce when borrower (junior vault) repays
    if (totalUsdcBorrowed() > ((totalAssets() - assets) * maxUtilizationBps) / MAX_BPS)
        revert MaxUtilizationBreached();
    // take out required assets from aave lending pool
    pool.withdraw(address(asset), assets, address(this));
}
```
DnGmxSeniorVault.sol#beforeWithdraw is called before each withdraw and will revert if the withdraw lowers the utilization of the vault below a certain threshold. This is problematic in the event that large deposits are required to maintain the stability of UXD.
UXD may become destabilized in the event that the senior vault has high utilization and the collateral is inaccessible

## Recommendation
I recommend three safeguards against this:
1) Monitor the current utilization of the senior vault and limit deposits if utilization is close to locking positions
2) Maintain a portion of the USDC deposits outside the vault (i.e. 10%) to avoid sudden potential liquidity crunches
3) Create functions to balance the proportions of USDC in and out of the vault to withdraw USDC from the vault in the event that utilization threatens to lock collateral
