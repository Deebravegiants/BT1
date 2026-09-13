# [H] _calculate_mintable_amount will return the wrong amount of shares if currentCollateralization != minimumCollateralization

## Summary
Severity: High
Reporter: 0x52
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L243-L256
Type: audit-issue

## Details
# _calculate_mintable_amount will return the wrong amount of shares if currentCollateralization != minimumCollateralization

## Summary

_calculate_mintable_amount only mints the correct number of shares if the currentCollateralization == minimumCollateralization. Otherwise it will mint too many shares and the excess debt will be socialized to the rest of the vault.

## Vulnerability Detail

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L243-L256

_calculate_mintable_amount uses the minimumCollateralization of the alchemistV2 to determine how many shares to mint to the recipient. If the currentCollateralization != minimumCollateralization then this will mint too much alETH to the recipient and the debt will be spread across all depositors.

Example:
Imagine there is currently 1 WETH deposited with 0.4 alETH minted. This gives a collateralization of 2.5. Now a new user deposits 1 WETH which will mint 0.5 alETH. This brings the collateralization to 2.22 and each position now effectively has a debt of 0.45 alETH. This pushes excess debt on the other use.

## Impact

Too many shares will be minted and previous depositors will be forced to pay for them

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L243-L256

## Tool used

Manual Review

## Recommendation

There are a few solutions to this:
1) Only mint at the current collateralization. This is the simplest and NFT sellers could receive slightly less than expected.
2) Rebalance the collateralization so that currentCollateralization == minimumCollateralization
