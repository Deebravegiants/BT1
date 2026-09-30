# [?] Fix ReentrancyGuard comments (#1084)

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2018-07-20
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/11266b0d56f19394a4fc983a334fe90a5da0bd98
Type: security-commit

## Details
Fix ReentrancyGuard comments (#1084)

## Patch
### contracts/ReentrancyGuard.sol
```diff
@@ -4,7 +4,7 @@ pragma solidity ^0.4.24;
 /**
  * @title Helps contracts guard against reentrancy attacks.
  * @author Remco Bloemen <remco@2π.com>
- * @notice If you mark a function `nonReentrant`, you should also
+ * @dev If you mark a function `nonReentrant`, you should also
  * mark it `external`.
  */
 contract ReentrancyGuard {
@@ -16,10 +16,10 @@ contract ReentrancyGuard {
 
   /**
    * @dev Prevents a contract from calling itself, directly or indirectly.
-   * @notice If you mark a function `nonReentrant`, you should also
-   * mark it `external`. Calling one nonReentrant function from
+   * If you mark a function `nonReentrant`, you should also
+   * mark it `external`. Calling one `nonReentrant` function from
    * another is not supported. Instead, you can implement a
-   * `private` function doing the actual work, and a `external`
+   * `private` function doing the actual work, and an `external`
    * wrapper marked as `nonReentrant`.
    */
   modifier nonReentrant() {
```
