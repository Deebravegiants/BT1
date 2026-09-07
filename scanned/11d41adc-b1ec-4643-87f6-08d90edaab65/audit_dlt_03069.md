# [M] YearnStrategy rounding down when calculating `toWithdraw` could result in insufficient withdrawal amount

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1239
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/yearn/YearnStrategy.sol#L140-L145


# Vulnerability details

## Impact

In YearnStrategy, when calculating the amount of shares to withdraw from YearnVault, the calculation rounds down. This could potentially result in an insufficient withdrawal amount.
```solidity
function _withdraw(
    address to,
    uint256 amount
) internal override nonReentrant {
    uint256 available = _currentBalance();
    require(available >= amount, "YearnStrategy: amount not valid");

    uint256 queued = wrappedNative.balanceOf(address(this));
    if (amount > queued) {
        uint256 pricePerShare = vault.pricePerShare();
        
        // @audit Round down when convert from amount -> share
        uint256 toWithdraw = (((amount - queued) *
            (10 ** vault.decimals())) / pricePerShare);

        vault.withdraw(toWithdraw, address(this), 0);
    }
    wrappedNative.safeTransfer(to, amount - 1); //rounding error

    emit AmountWithdrawn(to, amount);
}
```
Although the developers have acknowledged this by transferring only `amount - 1` at the end (with a "rounding error" comment), if the `pricePerShare` of a token is more than 2, for example, the rounding error could be more than 1 and it will always revert.

To summary, when `pricePerShare > 2 * 10 ** vault.decimals()`, `_withdraw()` will revert and block withdrawals.

## Proof of Concept

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1239_
