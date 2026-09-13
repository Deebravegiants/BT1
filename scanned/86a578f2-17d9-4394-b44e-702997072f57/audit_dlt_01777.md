# [?] Fix panic on closing nil db  (#3175)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2021-11-03
Source: https://github.com/algorand/go-algorand/commit/009b7981e1245180ccae5be93674e643157aad26
Type: security-commit

## Details
Fix panic on closing nil db  (#3175)

## Summary

FillDBWithParticipationKeys will return empty PersistedParticipation when lastValid is less than firstValid.
When this happens, newPart will not have partdb in newPart.Store, instead, will have an empty object.
Calling Close on the empty object will call close on nil Accessor pointer and panic.

This change avoids using the returned object with non-nil error, and properly closes the db with the valid object.
## Test Plan

Added test to verify the proper handling of the different errors returned from FillDBWithParticipationKeys and handled by GenParticipationKeysTo.
