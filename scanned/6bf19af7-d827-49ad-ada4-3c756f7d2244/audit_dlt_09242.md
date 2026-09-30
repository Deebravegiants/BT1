# [?] Merge pull request #604 from elopio/tests/fix-ReentrancyGuard

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2017-12-22
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/4ce0e211c500aa756120c4f2851cc75518123309
Type: security-commit

## Details
Merge pull request #604 from elopio/tests/fix-ReentrancyGuard

test: fix the mocks path in ReentrancyGuard test

## Patch
### test/ReentrancyGuard.test.js
```diff
@@ -1,7 +1,7 @@
 
 import expectThrow from './helpers/expectThrow';
-const ReentrancyMock = artifacts.require('./helper/ReentrancyMock.sol');
-const ReentrancyAttack = artifacts.require('./helper/ReentrancyAttack.sol');
+const ReentrancyMock = artifacts.require('./mocks/ReentrancyMock.sol');
+const ReentrancyAttack = artifacts.require('./mocks/ReentrancyAttack.sol');
 
 contract('ReentrancyGuard', function (accounts) {
   let reentrancyMock;
```
