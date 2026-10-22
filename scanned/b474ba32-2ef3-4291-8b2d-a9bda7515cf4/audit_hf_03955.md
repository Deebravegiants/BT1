# [M] navPerShareHighMark not reset to 1.0

## Summary
Severity: Medium
Contest weight: 0.5988
Dataset id: 20301
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LMPVault will only collect fees if the current NAV (currentNavPerShare) is more than the last NAV (effectiveNavPerShareHighMark).
3-07-14/src/vault/LMPVault.sol#L800
File: LMPVault.sol
```solidity
function _collectFees(uint256 idle, uint256 debt, uint256 totalSupply) internal {
    address sink = feeSink;
    uint256 fees = 0;
    uint256 shares = 0;
    uint256 profit = 0;

    // If there's no supply then there should be no assets and so nothing
    // to actually take fees on
    if (totalSupply == 0) {
        return;
    }

    uint256 currentNavPerShare = ((idle + debt) * MAX_FEE_BPS) /
        totalSupply;
    uint256 effectiveNavPerShareHighMark = navPerShareHighMark;

    if (currentNavPerShare > effectiveNavPerShareHighMark) {
        // Even if we aren't going to take the fee (haven't set a sink)
        // We still want to calculate so we can emit for off-chain analysis
        profit = (currentNavPerShare - effectiveNavPerShareHighMark) *
            totalSupply;
```
Assume the current LMPVault state is as follows:
• totalAssets = 15 WETH
• totalSupply = 10 shares
• NAV/share = 1.5
• effectiveNavPerShareHighMark = 1.5
Alice owned all the remaining shares in the vault, and she decided to withdraw all her 10 shares. As a result, the totalAssets and totalSupply become zero. It was found that when all the shares have been exited, the effectiveNavPerShareHighMark is not automatically reset to 1.0.
Assume that at some point later, other users started to deposit into the LMPVault, and the vault invests the deposited WETH to profitable destination vaults, resulting in the real/actual NAV rising from 1.0 to 1.49 over a period of time.
The system is designed to collect fees when there is a rise in NAV due to profitable investment from sound rebalancing strategies. However, since the effectiveNavPerShareHighMark has been set to 1.5 previously, no fee is collected when the NAV rises from 1.0 to 1.49, resulting in a loss of fee.
Loss of fee. Fee collection is an integral part of the protocol; thus the loss of fee is considered a High issue.

## Recommendation
Consider resetting the navPerShareHighMark to 1.0 whenever a vault has been fully exited.
```solidity
function _withdraw(
    uint256 assets,
    uint256 shares,
    address receiver,
    address owner
) internal virtual returns (uint256) {
    ..SNIP..
    _burn(owner, shares);
    if (totalSupply() == 0) navPerShareHighMark = MAX_FEE_BPS;
    emit Withdraw(msg.sender, receiver, owner, returnedAssets, shares);
    _baseAsset.safeTransfer(receiver, returnedAssets);
    return returnedAssets;
}
```
