# [?] [master] Fix the problem with JSON parser crashing (#3015)

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/Zilliqa
Published: 2022-09-23
Source: https://github.com/Zilliqa/zq1/commit/4369ad08fa2fa1323d3d6833de73f25bc75e4e76
Type: security-commit

## Details
[master] Fix the problem with JSON parser crashing (#3015)

* Upgrade Nlohmann JSON parser

* Attempting another fix + log the value

* Another possible fix

* Remove extra multithreading in eth_call

* cleanup of code, implement async to call evm-ds, eth_call ut for failure and timeouts

* add lock to prevent crashing

* Fix the problem in the way of f51c51fd4

* Disable timeout unit test, as we decided to ignore eth_call timeouts for now

Co-authored-by: michel <michel@zilliqa.com>
