# [M] 7.8 Potentially Incorrect Strategy Report

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 2 Code Corrected

Calling the harvest function on a strategy contract may result in a bad report to the pool manager. If the
reward token the keepers receive is equal to the want token of the strategy, then the transfer to the
keeper can be successful even though no specific allocation of funds to the strategy for the rewards was
made. Incorrectly, the keeper's fee will still be part of the reported profit as the profit is computed
beforehand and not adjusted.

Code corrected:

In the constructor of the strategy it checked that want and reward token are not the same.
