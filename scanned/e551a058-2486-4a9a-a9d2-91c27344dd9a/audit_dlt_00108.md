# [C] SA003

## Summary
Severity: Critical
Chain: Namada
Component: anoma/namada
Published: 2025-02-17
Source: https://github.com/namada-net/namada/security/advisories/GHSA-2gw2-qgjg-xh6p
Type: github-advisory

## Details
### Impact

Ledger crash. A user is able to initialize a post-genesis validator with a negative commission rate using the `--force` flag. If this validator gets into the consensus set, then when computing PoS inflation inside `fn update_rewards_products_and_mint_inflation`, an instance of `mul_floor` will cause the return of an `Err`, which causes `finalize_block` to error.

### Patches

This issue has been patched in apps version 1.1.0. The PoS validity predicate now enforces that the commission rate is not negative and any transaction that fails the check will be rejected, both for newly initialized validators and for commission rate change of an existing validator.

### Workarounds

There are no workarounds and users are advised to upgrade.
