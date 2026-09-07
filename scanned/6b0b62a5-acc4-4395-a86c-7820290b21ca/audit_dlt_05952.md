# [?] Fix reentrancy vulnerability in example Crowfund.refund() (#2739)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2022-04-01
Source: https://github.com/vyperlang/vyper/commit/7f7379b89857c630e8ddca4e8173d8bde391cd0a
Type: security-commit

## Details
Fix reentrancy vulnerability in example Crowfund.refund() (#2739)

* Fix reentrancy vulnerability Crowfund.refund()

* Refactor crowdfund to his own folder

* Fix vulnerability REVERT on send() can prevent refund

* Fix one participation can participate multiple time

* Use 0 instead of empty; Put crowdfund outside of  folder

Co-authored-by: hitsuzen <hitsuzen@mail.com>
