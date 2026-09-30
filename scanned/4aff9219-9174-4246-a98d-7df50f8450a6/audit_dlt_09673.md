# [?] fix underflow in test

## Summary
Severity: Unknown
Chain: EigenLayer
Component: Layr-Labs/eigenlayer-contracts
Published: 2023-05-16
Source: https://github.com/Layr-Labs/eigenlayer-contracts/commit/a479d74924e4f46b098ebb6481b876236928a9a0
Type: security-commit

## Details
fix underflow in test

## Patch
### src/test/unit/StrategyBaseTVLLimitsUnit.sol
```diff
@@ -118,6 +118,9 @@ contract StrategyBaseTVLLimitsUnitTests is Test {
         strategy.setTVLLimits(maxPerDeposit, maxDeposits);
         cheats.stopPrank();
 
+        // we need to actually transfer the tokens to the strategy to avoid underflow in the `deposit` calculation
+        underlyingToken.transfer(address(strategy), depositAmount);
+
         uint256 sharesBefore = strategy.totalShares();
         cheats.startPrank(address(strategyManager));
         strategy.deposit(underlyingToken, depositAmount);
```
