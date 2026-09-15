# [M] Tests should not fail

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The role of the tests should be to make sure the application behaves properly. This should include positive tests (functionality that should be implemented) and negative tests (behavior stopped or limited by the application).

The test suite should pass 100% of the tests. After spending time with the development team, we managed to ask for the changes that allowed us to run the tests suite. This revealed that out of the 555 tests, 206 are failing. This staggering number does not allow us to check what the problem is and makes anybody running tests ignore them completely.

Tests should be an integral part of the codebase, and they should be considered as important (or even more important) than the code itself. One should be able to recreate the whole codebase by just having the tests.

#### Recommendation

Update tests in order for the whole of the test suite to pass.
