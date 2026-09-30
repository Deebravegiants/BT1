# [?] Now setting the finalized flag before doing finalization to prevent possbile reentrancy issues. (#1447)

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2018-10-18
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/5bb865218f02a01d0521c9d9a947cdf4bd32e74c
Type: security-commit

## Details
Now setting the finalized flag before doing finalization to prevent possbile reentrancy issues. (#1447)

## Patch
### contracts/crowdsale/distribution/FinalizableCrowdsale.sol
```diff
@@ -34,10 +34,10 @@ contract FinalizableCrowdsale is TimedCrowdsale {
     require(!_finalized);
     require(hasClosed());
 
+    _finalized = true;
+
     _finalization();
     emit CrowdsaleFinalized();
-
-    _finalized = true;
   }
 
   /**
@@ -47,5 +47,4 @@ contract FinalizableCrowdsale is TimedCrowdsale {
    */
   function _finalization() internal {
   }
-
 }
```
