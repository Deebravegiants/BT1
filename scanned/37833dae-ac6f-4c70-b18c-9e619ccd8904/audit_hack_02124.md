# [M] Manager can grief with fees

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Handle

@cmichelio


# Vulnerability details


## Vulnerability Details

The fees in `NFTXVaultUpgradeable` can be set arbitrarily high (no restriction in `setFees`).

## Impact

The manager can frontrun mints and set a huge fee (for example `fee = base`) which transfers user's NFTs to the vault but doesn't mint any pool share tokens in return for the user.

Similar griefing attacks are also possible with other functions besides `mint`.


## Recommended Mitigation Steps

Check for a max fee as a percentage of `base` (like 10%) whenever setting fees.
