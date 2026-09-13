# [H] Missing access restriction on `NFTXVaultUpgradeable.finalizeFund`

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-nftx
Published: 2021-05-11
Source: https://github.com/code-423n4/2021-05-nftx-findings/issues/50
Type: code-finding

## Details
# Handle

@cmichelio


# Vulnerability details


## Vulnerability Details

Missing access restriction on `NFTXVaultUpgradeable.finalizeFund`.

## Impact

Anyone can lock out the manager by calling `finalizeFund` which sets the manager to 0.
This griefing attack can prevent managers from setting correct fees, vault features, eligibility modules, etc. on the Vault which then needs to be redeployed (but users could have already deposited tokens) or go through a lengthy governance process and let the owner restore the manager but then `finalizeFund` can just be called again.


## Recommended Mitigation Steps

Make `finalizeFund` only callable by the manager.
