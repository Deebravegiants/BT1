# [M] Incomplete test suite

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
The testing suite covering in-scope contracts is incomplete. Although `OgvStaking.t.sol` and `Rewards.t.sol` test files were provided, the instructions in the `README` for the project do not sufficiently provide guidance on how to run comprehensive tests for the repo.

As the test suite was left outside the audit’s scope, please consider thoroughly reviewing the test suite to make sure all tests run successfully after following the instructions in the `README` file. Extensive unit tests aiming at 95% coverage are recommended in order for the security of the project to be assessed in a future audit. Integrating test coverage reports in every single pull request of the project is also highly advisable.

**Update**: _Fixed in pull request [#100](https://github.com/OriginProtocol/ousd-governance/pull/100/)._
