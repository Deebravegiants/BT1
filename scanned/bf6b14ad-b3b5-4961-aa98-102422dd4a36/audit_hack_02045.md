# [M] 6.4 Expired Slashing Proposals Are Not Purged

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

When purgePendingSlashings is called (Validators and Roots), only proposals with state
REJECTED or EXECUTED are deleted. The proposals with state EXPIRED are kept in the
pendingSlashingProposals list and their slashing amount is always kept into account when
calculating the pending slashing amount. Thus, preventing the Roots and Validators to withdraw this
amount that they should be able to withdraw, locking it forever.

Code corrected :

RootNodesSlashingVoting and ValidatorsSlashingVoting now define slashingAffectsWithdrawal
functions. The slashingAffectsWithdrawal function includes a check that slashing proposal is not
in EXPIRED state.
