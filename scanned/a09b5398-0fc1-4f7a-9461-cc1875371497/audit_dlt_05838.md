# [?] Fix potential deadlock (#5124)

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2024-11-06
Source: https://github.com/XRPLF/rippled/commit/9e48fc0c834e8a6e340c521e9ec58b97b944c1fd
Type: security-commit

## Details
Fix potential deadlock (#5124)

* 2.2.2 changed functions acquireAsync and NetworkOPsImp::recvValidation to add an item to a collection under lock, unlock, do some work, then lock again to do remove the item. It will deadlock if an exception is thrown while adding the item - before unlocking.
* Replace ScopedUnlock with scope_unlock.
