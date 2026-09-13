# [H] Vault#migrate isn't able to do anything because it lacks any kind of approvals to migrator

## Summary
Severity: High
Reporter: 0x52
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L546-L556
Type: audit-issue

## Details
# Vault#migrate isn't able to do anything because it lacks any kind of approvals to migrator

## Summary

Vault#migrate is designed to somehow migrate the position of the vault somewhere new. The problem is that the migrator is never approve to move any tokens on behalf of Vault. The result is that calling migrator#migrate can't actually do anything with any of the Vault's tokens. In a scenario that the vault needs to be migrated it will likely result in all user funds becoming locked and unrecoverable.

## Vulnerability Detail

See summary

## Impact

Vault#migrate isn't able to do anything and will cause serious issues if there is ever a need to migrate

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L546-L556

## Tool used

Manual Review

## Recommendation

Before calling migrator#migrate make sure to grant all relevant approvals:

    +   ERC20(WETH).approve(self.migrator, max_value(uint256))
    +   ERC20(ALCX_YVWETH).approve(self.migrator, max_value(uint256))
    +   alchemist.approveBurn(self.migrator, max_value(uint256))
