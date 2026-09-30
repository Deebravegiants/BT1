# [?] Fix ReentrancyGuard for Proxy Pattern (#2171)

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2020-05-12
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/cfa9ad9943f24810f69714907395b63f90040044
Type: security-commit

## Details
Fix ReentrancyGuard for Proxy Pattern (#2171)

* Fix ReentrancyGuard for Proxy Pattern

* Update ReentrancyGuard.sol

* Change constant values

* Add changelog entry

Co-authored-by: Nicolás Venturo <nicolas.venturo@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -3,6 +3,7 @@
 ## 3.1.0 (unreleased)
 
 ### Improvements
+ * `ReentrancyGuard`: reduced overhead of using the `nonReentrant` modifier. ([#2171](https://github.com/OpenZeppelin/openzeppelin-contracts/pull/2171))
  * `AccessControl`: added a `RoleAdminChanged` event to `_setAdminRole`. ([#2214](https://github.com/OpenZeppelin/openzeppelin-contracts/pull/2214))
 
 ## 3.0.1 (2020-04-27)
```

### contracts/utils/ReentrancyGuard.sol
```diff
@@ -17,16 +17,24 @@ pragma solidity ^0.6.0;
  * https://blog.openzeppelin.com/reentrancy-after-istanbul/[Reentrancy After Istanbul].
  */
 contract ReentrancyGuard {
-    bool private _notEntered;
+    // Booleans are more expensive than uint256 or any type that takes up a full
+    // word because each write operation emits an extra SLOAD to first read the
+    // slot's contents, replace the bits taken up by the boolean, and then write
+    // back. This is the compiler's defense against contract upgrades and
+    // pointer aliasing, and it cannot be disabled.
+
+    // The values being non-zero value makes deployment a bit more expensive,
+    // but in exchange the refund on every call to nonReentrant will be lower in
+    // amount. Since refunds are capped to a percentage of the total
+    // transaction's gas, it is best to keep them low in cases like this one, to
+    // increase the likelihood of the full refund coming into effect.
+    uint256 private constant _NOT_ENTERED = 1;
+    uint256 private constant _ENTERED = 2;
+
+    uint256 private _status;
 
     constructor () internal {
-        // Storing an initial non-zero value makes deployment a bit more
-        // expensive, but in exchange the refund on every call to nonReentrant
-        // will be lower in amount. Since refunds are capped to a percetange of
-        // the total transaction's gas, it is best to keep them low in cases
-        // like this one, to increase the likelihood of the full refund coming
-        // into effect.
-        _notEntered = true;
+        _status = _NOT_ENTERED;
     }
 
     /**
@@ -38,15 +46,15 @@ contract ReentrancyGuard {
      */
     modifier nonReentrant() {
         // On the first call to nonReentrant, _notEntered will be true
-        require(_notEntered, "ReentrancyGuard: reentrant call");
+        require(_status != _ENTERED, "ReentrancyGuard: reentrant call");
 
         // Any calls to nonReentrant after this point will fail
-        _notEntered = false;
+        _status = _ENTERED;
 
         _;
 
         // By storing the original value once again, a refund is triggered (see
         // https://eips.ethereum.org/EIPS/eip-2200)
-        _notEntered = true;
+        _status = _NOT_ENTERED;
     }
 }
```
