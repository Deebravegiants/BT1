# [M] 6.4 Share Distribution Depends on First Deposit

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

The user's shares when depositing an amount of yETH are calculated as:

```
_assets * _total_shares / _total_assets
```
However, in the case of the first deposit, the number of assets deposited is the number of shares the user
receives. In case a user deposits a very small amount (at best 1 WEI), they would receive 1 share. When
the total assets increase because profits are made, the fraction _total_shares / _total_assets
will become 0 for amounts smaller than _total_assets. Additionally, when adding assets, they need
to be multiples of _total_assets. Hence, the first deposit determines the minimum step size or
rounding error for the following deposits.

The was independently reported by Yearn while the review was ongoing.

Code corrected:

Yearn implemented a practical solution by specifying a minimum deposit amount
MINIMUM_INITIAL_DEPOSIT of 1e15 which makes the attack unlikely in practice. However, we would
like to highlight that the core issue is still present even with this practical mitigation. The issue arises only
in case of a high discrepancy between the first deposit and the potential rewards which now should be
higher by a factor of 1e15.
