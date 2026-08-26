# [?] types: prevent spurious validator power overflow warnings when changing the validator set (#4183)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2019-11-26
Source: https://github.com/cometbft/cometbft/commit/759ccebe54fb008e2e4947250e389aa55b013893
Type: security-commit

## Details
types: prevent spurious validator power overflow warnings when changing the validator set (#4183)

Fix for #4164
The general problem is that in certain conditions an overflow warning is issued when attempting to update a validator set even if the final set's total voting power is not over the maximum allowed.
Root cause is that in verifyUpdates(), updates are verified wrt to total voting power in the order of validator address. It is then possible that a low address validator may increase its power such that the temporary total voting power count goes over MaxTotalVotingPower.

Scenarios where removing and adding/ updating validators with high voting power, in the same update operation, cause the same false warning and the updates are not applied.

Main changes to fix this are in verifyUpdate() that now does the verification starting with the decreases in power. It also takes into account the removals that are part of the update.

## Commits:

* tests for overflow detection and prevention

* test fix

* more tests

* fix the false overflow warnings and golint

* scopelint warning fix

* review comments

* variant with using sort by amount of change in power

* compute separately number new validators in update

* types: use a switch in processChanges

* more review comments

* types: use HasAddress in numNewValidators

* types: refactor verifyUpdates

copy updates, sort them by delta and use resulting slice to calculate
tvpAfterUpdatesBeforeRemovals.

_Trimmed to 38 lines — full report: https://github.com/cometbft/cometbft/commit/759ccebe54fb008e2e4947250e389aa55b013893_
