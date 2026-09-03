# [M] ERC4626 does not work with fee-on-transfer tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-tribe-turbo
Published: 2022-02-20
Source: https://github.com/code-423n4/2022-02-tribe-turbo-findings/issues/26
Type: code-finding

## Details
# Lines of code

https://github.com/Rari-Capital/solmate/blob/8c0e278900fe552fa0739975bde21c6a07d84ccf/src/mixins/ERC4626.sol#L52


# Vulnerability details

## Impact
> The docs/video say `ERC4626.sol` is in scope as its part of `TurboSafe`

The `ERC4626.deposit/mint` functions do not work well with fee-on-transfer tokens as the `amount` variable is the pre-fee amount, including the fee, whereas the `totalAssets` do not include the fee anymore.

This can be abused to mint more shares than desired.

```solidity
function deposit(uint256 amount, address to) public virtual returns (uint256 shares) {
    // Check for rounding error since we round down in previewDeposit.
    require((shares = previewDeposit(amount)) != 0, "ZERO_SHARES");

    // Need to transfer before minting or ERC777s could reenter.
    asset.safeTransferFrom(msg.sender, address(this), amount);

    _mint(to, shares);

    emit Deposit(msg.sender, to, amount, shares);

    afterDeposit(amount, shares);
}
```

#### POC
A `deposit(1000)` should result in the same shares as two deposits of `deposit(500)` but it does not because `amount` is the pre-fee amount.
Assume a fee-on-transfer of `20%`. Assume current `totalAmount = 1000`, `totalShares = 1000` for simplicity.

- `deposit(1000) = 1000 / totalAmount * totalShares = 1000 shares`
- `deposit(500) = 500 / totalAmount * totalShares = 500 shares`. Now the `totalShares` increased by 500 but the `totalAssets` only increased by `(100% - 20%) * 500 = 400`. Therefore, the second `deposit(500) = 500 / (totalAmount + 400) * (newTotalShares) = 500 / (1400) * 1500 = 535.714285714 shares`.

In total, the two deposits lead to `35` more shares than a single deposit of the sum of the deposits.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-02-tribe-turbo-findings/issues/26_
