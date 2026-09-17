# [M] 6.35 Transferring Tokens Only to lowerVault

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

The following code should transfer tokens from erc20Vault to the two Uniswap vaults with the
respective amounts:

```
if (!isNegativeCapitalDelta) {
totalPulledAmounts = erc20Vault.pull(
address(lowerVault),
tokens,
lowerTokenAmounts,
_makeUniswapVaultOptions(minLowerVaultTokens, deadline)
);
pulledAmounts = erc20Vault.pull(
address(lowerVault),
tokens,
upperTokenAmounts,
_makeUniswapVaultOptions(minUpperVaultTokens, deadline)
);
for (uint256 i = 0; i < 2; i++) {
totalPulledAmounts[i] += pulledAmounts[i];
}
}
```
Both transfers above are from the erc20Vault to the lowerVault, hence no tokens are transferred to
the upperVault.

Code corrected:

The bug has been fixed, the code now transfers the respective amounts to the lowerVault and
upperVault.
