# [M] Deflation attack

## Summary
Severity: Medium
Contest weight: 0.3276
Dataset id: 2350
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The flow of assets between SiloVault and its markets favour the markets (per standard ERC4626 specifications). This means that SiloVault can lose assets compared to its total supply of shares. This deflates the share price. At low total asset levels, this can be exploited to deflate the share price until the shares per asset is close to overflowing.

This can be exploited to either simply brick the vault, or such that the attacker is the guaranteed sole holder and recipient of the incentive rewards.

## Proof of Concept
The shares minted is calculated as `_assets.mulDiv(_newTotalSupply + 10 ** _decimalsOffset(), _newTotalAssets + 1, _rounding)`, where the [total assets](https://github.com/code-423n4/2025-03-silo-finance/blob/0409be5b85d7aabfbbe10de1de1890d4b862d2d5/silo-vaults/contracts/SiloVault.sol#L647-L652) is based on the redeemable value of all market shares held by SiloVault.

For example, the first depositor deposits 1 wei into SiloVault, which deposits this into a market, and mints `10 ** _decimalsOffset()` shares. The market, however, is likely to round this away and not return any share to SiloVault. On the next deposit into SiloVault, `totalAssets` is zero, but `10 ** _decimalsOffset()` shares were minted. Again depositing 1 wei mints `2 * 10 ** _decimalsOffset()`, without increasing `totalAssets`. Each repetition doubles the total supply.

The same would, of course, happen if `totalAssets` on deposit did increase to `1` but due to the market updating its price, this later became `0`.

Suppose SiloVault were to instead mint shares according to the increase in `totalAssets`. Then no shares would be minted in the above example. Suppose then instead 10 wei are deposited into SiloVault, which deposits this into a market, in return, for 8 market shares (let’s say the market’s price is 1.13 assets/share). This is redeemable for 9 asset tokens, so SiloVault mints `9 * 10 ** _decimalsOffset()` shares. Now, redeeming `8 * 10 ** _decimalsOffset()` shares from SiloVault makes SiloVault withdraw 8 asset tokens from the market. Withdrawing 8 asset tokens burns not 7.08 but all 8 market shares, and SiloVault is now, just as above, left with zero totalAssets but a total supply of `1 * 10 ** _decimalsOffset()`.

## Recommendation
No recommendation
