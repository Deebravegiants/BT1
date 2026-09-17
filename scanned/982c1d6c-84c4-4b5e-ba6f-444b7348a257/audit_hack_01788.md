# [M] Increase test coverage

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Test coverage is fairly limited.
LPStaking tests only cover the happy path.
StakeLPCoreV8 has no tests.
Many test descriptions are inaccurate.


#### Examples

Test description inaccuracy examples:

- This tests that a Staker can mint new tokens, but does not check to make sure that Stakers are the ONLY group that can mint. LiquidStakingTest.js#L82

- This test only shows that an unauthorized address can't use the stake function to mint tokens. LiquidStakingTest.js#L99

- This test actually tests for the inverse case. STokensTest.js#L82
<!--
Code URLs get formatted nicely, i.e. Vulnerable.sol#L27-L33
-->

#### Recommendation

Increase test coverage for entire codebase.
Add tests for the inherited contracts from OpenZeppelin.
Test for edge cases, and multiple expected cases.
Ensure that the test description matches the functionality that is actually tested.

<!-- Supply advice on how to best fix the problem. -->
