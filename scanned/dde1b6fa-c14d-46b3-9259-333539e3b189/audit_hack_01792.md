# [M] Insufficient tests

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
It is crucial to write tests with possibly 100% coverage for smart contract systems. Given that BTCPlus has inner complexity and also integrates many DeFi projects, using unit testing and fuzzing in all code paths is essential to a secure system.

Currently there are only 63 unit tests (with 1 failing) for the main components (Plus/Composite token, Governance, Liquidity Gauge, etc) which are only testing the predetermined code execution paths. There are also DeFi protocol specific tests that are not well organized to be able to find the coverage on the system.


#### Recommendation

Write proper tests for all possible code flows and specially edge cases (Price volatility, token transfer failure, 0 amounts, etc). It is useful to have one command to run all tests and have a code coverage report at the end. Also using libraries like eth-gas-reporter it's possible to know the gas usage of different functionalities in order to optimize and prevent lock ups in the future.
