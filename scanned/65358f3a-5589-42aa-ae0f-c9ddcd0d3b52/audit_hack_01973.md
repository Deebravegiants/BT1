# [M] 6.25 Conflicting Specifications for MStrategy

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Specification Changed

The specifications of MStrategy have conflicting instructions. The section "TickMin and TickMax update"
states:

```
tickMin and tickMax are initially set to some ad-hoc params.
As soon as the current price — tick is greater than tickMax - tickNeiborhood
or less than tickMin + tickNeiborhood the boundaries of the interval
is expanded by tickIncrease amount.
```
In the rebalance steps, tickNeiborhood is used instead of tickIncrease:

- tick is greater than tickMax - tickNeiborhood then new
boundaries are [tickMin, tickMax + tickNeiborhood]
- tick is less than tickMin + tickNeiborhood then new
boundaries are [tickMin - tickNeiborhood, tickMax]

Specification changed:

The specification was changed accordingly.
