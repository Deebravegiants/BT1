# [M] Vault.vy doesn't implement proper precautions if the Alchemix TVL changes

## Summary
Severity: Medium
Reporter: 0x52
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L262-L278
Type: audit-issue

## Details
# Vault.vy doesn't implement proper precautions if the Alchemix TVL changes

## Summary

Authors acknowledge that the Vault.vy contract will need to be redeployed if there is a change in TVL but they don't have the proper precautions in the contract should it change and auctions complete before the new contract is deployed and switched.

## Vulnerability Detail

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L262-L278

If the TVL decreases then the check in Vault.vy#_calculate_max_mintable_amount will result in the recipient receiving less funds than expected. If the TVL decreases then the recipient will receive more funds than expected and the extra TVL will be socialized across the other depositors and they will collectively pay for the extra funds dispersed.

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394-L404

The other problem is that if the TVL increases new deposits can also call Vault.vy#withdraw_underlying_to_claim to extract further funds from other depositors.

Example:
Assume the original minimumCollateralization = 50%. User A deposits 1 ETH, which pays 0.5 alETH to the recipient. Later the minimumCollateralization decreses to 40%. User B deposits 1 ETH which pays 0.66 ETH to the recipient. The issue is that debt is socialized across both users and each user now has a debt of 0.583. This unfairly results in User A having more debt than they should. 

The second problem is with withdraw_underlying_to_claim. Since it is permissionless a user can now withdraw an additional 0.1733 ETH since the max debt is now 1.33 and the current debt is only 1.16. This amount is evenly distributed across all positions allows User B to claim an additional 0.086 ETH.

## Impact

Losses to either recipient or previous depositors

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L262-L278

## Tool used

Manual Review

## Recommendation

Cache the minimumCollateralization in the constructor and cause all deposits/claims to revert if the fresh minimumCollateralization is ever different from the cached value.
