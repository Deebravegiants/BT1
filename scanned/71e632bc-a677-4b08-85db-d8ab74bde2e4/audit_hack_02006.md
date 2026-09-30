# [M] 6.4 Update of unlockTime

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Specification Changed

We do not have sufficient specification about the intended behavior, but the following seems to be an
issue. The internal function _lockFXS updates the unlockTime if the following condition is satisfied:

```
if (unlockInWeeks.sub(unlockTime) > 1) {
ILocker(locker).increaseUnlockTime(unlockAt);
unlockTime = unlockInWeeks;
}
```
Given that both unlockInWeeks and unlockTime store the number of seconds passed until a given
week, the comparison with 2 (sec) seems incorrect.

Specification changed

The current code will always evaluate the if condition as true if the comparison is bigger than 1.
StakeDAO changed the specification from two weeks to one week. Additionally, the 2 was changed to 1
(which has no effect but makes it more explicit). The code works but we need to highlight, that this only
works for one week check.
