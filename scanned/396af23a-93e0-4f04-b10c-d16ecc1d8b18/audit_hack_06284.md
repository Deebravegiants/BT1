# [H] Conversion from `int256` to `uint256` can break protocol functionality

## Summary
Severity: High
Reporter: Tricko
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L260-L278
Type: audit-issue

## Details
# Conversion from `int256` to `uint256` can break protocol functionality

## Summary
Possible conversion from negative `int256` to `uint256` will freeze contract main funcionality.

## Vulnerability Detail
Based on Alchemix docs "Debt is an int256 type that represents both the account's debt (positive values) and credit (negative values)", but the possibility of negative debt values is not dealt correctly in the code. On two places (`_calculate_max_mintable_amount` and `_latest_collateralisation`) the `int256` returned from `alchemist` is converted to an `uint256` using the builtin method `convert()`, but this explicit conversion only works for positive `int256`. If supplied with a negative `debt`, `convert(debt, uint256)` will revert.

If the contract manages to get to this state when debt values are negative, `Vault` functionality will get frozen, because `register_deposit` will always revert due to calling `_calculate_max_mintable_amount`. This state is irreversible, because the only way to fix this state is by minting more debt from `alchemist` until the actual debt `int256` value gets into positive range. But `Vault` only way to mint more debt is through `register_deposit`, that on this state will always revert. Therefore the contract stays indefinitely on this frozen state.

Because `_latest_collateralisation` will also revert, investors will be unable to `liquidate`, consequently their shares will be locked in the vault.

## Impact
As detailed above, if debt values manages to get negative, `Vault` will get permanently locked in a state when `register_deposit` will revert and investors won't be able to `liquidate` their shares, affecting the protocol funcionality.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L260-L278

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L355-L370
## Tool used
Manual Review 

## Recommendation
Instead of converting, consider using `int256` and handle edge cases where needed.
