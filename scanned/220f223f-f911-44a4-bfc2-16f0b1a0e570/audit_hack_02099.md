# [M] 7.1 Incorrect Description of Dog.bark()

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 2 Specification Changed

After the intermediate report the main functions of Liquidations 2.0 have been annotated with their
expected behavior taken from MIP45.

The description above Dog.bark() as well as the corresponding part in MIP45 are outdated: In order to
address an other issue (Liquidation of Dusty Vaults), the behavior has been slightly altered.

Notably, the statement

```
// There is a precondition about `room` that needs
// to be satisfied in order to create an auction:
// room > 0 && room >= ilk.dust
// otherwise the transaction fails
```
no longer applies in the updated code.

Specification changed:

The code comments have been changed and now explain the new liquidation behaviour including the
preconditions.
