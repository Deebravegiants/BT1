# [M] Vault can be changed during an auction

## Summary
Severity: Medium
Reporter: kiki_dev
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L300
Type: audit-issue

## Details
# Vault can be changed during an auction

## Summary
Set vault can be changed during an auction. If this were to happen it would divide the were the money is being stored into multiple vaults. This will affect how much value each person's share is. Which can lead to users being able to liquidate more than they should be allowed to at the expense of other users. 
## Vulnerability Detail
See Summary

## Impact
Loss of funds for some users.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L300

## Tool used

Manual Review

## Recommendation
While auction is open the `set_vault` function should revert. This would prevent vault funds being split into multiple. Even adding `epoch_in_progress()` would be sufficient.
