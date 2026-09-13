# [?] consensus: Fix a rare crash bug

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2021-07-26
Source: https://github.com/dogecoin/dogecoin/commit/14a2e1ba9644d0cc59c1f773d330a8f2674ab54b
Type: security-commit

## Details
consensus: Fix a rare crash bug

Fix a rare crash bug where no best chain can be activated, and therefore when trying
to find the height of the best chain via the last block triggers a null pointer dereference.
