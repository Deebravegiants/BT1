# [M] adminAccountMigration

## Summary
Severity: Medium
Contest weight: 0.1357
Dataset id: 1595
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `adminAccountMigration()` function is called by the operator role to update all sellers’ auctions. The `auction.seller` account is updated to the new address, however, the protocol fails to update `buyPrice.seller`. As a result, the protocol is put in a deadlock situation where the new address cannot cancel the auction and withdraw their NFT without the compromised account first cancelling the buy price and vice-versa. This is only recoverable if the new account is migrated back to the compromised account and then `cancelBuyPrice()` is called before migrating back.

## Recommendation
Consider invalidating the buy offer before account migration.
Correct - if we were to use `adminAccountMigration` while the NFT had both an auction reserve price and had a buy price set this would have created a deadlock type situation where the NFT is in a bad state and we’d likely need to migrate the NFT back to the original owner in order to correct it.

There were two possible solutions to this:

  * Update `adminAccountMigration` to update both auction and buy price at the same time.
  * Cut `adminAccountMigration` completely.

We went with the latter solution. This is not a feature we have used in some time and as we continue to grow, it’s not scalable since it required Foundation to get involved directly and included manual verification steps.

Removing this feature has saved over 2KB in contract space as well, which we really needed in order to make room for new features and changes.
