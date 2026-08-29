# [?] AA-465: Use transient storage for reentrancy guard (#515)

## Summary
Severity: Unknown
Chain: ERC-4337
Component: eth-infinitism/account-abstraction
Published: 2024-12-29
Source: https://github.com/eth-infinitism/account-abstraction/commit/b3bae63bd9bc0ed394dfca8668008213127adb62
Type: security-commit

## Details
AA-465: Use transient storage for reentrancy guard (#515)

* AA-466: Prevent InitCode frontrunning; AA-470: Make SenderCreator public

* Update minimum Solidity compiler version to 0.8.28

* Update Node.js version used in GitHub actions

* Use ReentrancyGuardTransient in the EntryPoint

* Update solidity-coverage to version 0.8.14

* Skip 'TokenPaymaster' test for the 'coverage' task

---------

Co-authored-by: Dror Tirosh <dror.tirosh@gmail.com>
