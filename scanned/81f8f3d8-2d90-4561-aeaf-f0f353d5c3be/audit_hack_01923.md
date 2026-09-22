# [H] 6.1 Double Counting During Maple Migration

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

During the migration of Maple positions, double counting of Maple LP tokens is possible as there are no
restrictions enforced on lend().

Consider the following scenario:

```
1.The position holds 10 v1 LP tokens.
2.The snapshot is taken and snapshots are frozen.
3.The airdrop of v2 LP tokens happens and the position receives 10 v2 LP tokens. Note that
getManagedAssets() does not consider v2 LP tokens since the v2 pool is not tracked. Hence,
the valuation is 10 v1 LP tokens.
4.The manager lends tokens to Maple v2 and creates 10 v2 LP tokens. Now,
getManagedAssets() considers both v1 and v2 LP tokens since lending will start tracking the v
pool. Hence, the valuation is 10 v1 LP tokens and 20 v2 LP tokens.
```
Thus, funds could be overvalued between airdop and migration execution.

Code corrected:

Lending is now only allowed if the position has been migrated.
