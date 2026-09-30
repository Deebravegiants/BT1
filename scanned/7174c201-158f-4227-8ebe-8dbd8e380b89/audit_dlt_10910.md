# [?] NODE-1526: UTX pool overflow bypass fixes

## Summary
Severity: Unknown
Chain: Waves
Component: wavesplatform/Waves
Published: 2019-03-19
Source: https://github.com/wavesplatform/Waves/commit/a9a2712dc065b0f09b3d231ed7d75089ea0e0e88
Type: security-commit

## Details
NODE-1526: UTX pool overflow bypass fixes

## Patch
### src/test/scala/com/wavesplatform/utx/UtxPoolSpecification.scala
```diff
@@ -397,7 +397,7 @@ class UtxPoolSpecification extends FreeSpec with Matchers with MockFactory with
         val Some((account, block, scripted, unscripted)) = generateBlock.sample
         d.blockchainUpdater.processBlock(block) shouldBe 'right
 
-        val utx = new UtxPoolImpl(ntpTime, d.blockchainUpdater, ignoreSpendableBalanceChanged, FunctionalitySettings.TESTNET, UtxSettings(9999999, PoolDefaultMaxBytes, Set.empty, Set.empty, allowTransactionsFromSmartAccounts = true))
+        val utx = new UtxPoolImpl(ntpTime, d.blockchainUpdater, ignoreSpendableBalanceChanged, FunctionalitySettings.TESTNET, UtxSettings(9999999, PoolDefaultMaxBytes, 999999, Set.empty, Set.empty, allowTransactionsFromSmartAccounts = true, allowSkipChecks = false))
         all((scripted ++ unscripted).map(utx.putIfNew)) shouldBe 'right
 
         val constraint = MultiDimensionalMiningConstraint(NonEmptyList.of(OneDimensionalMiningConstraint(1, TxEstimators.scriptRunNumber), OneDimensionalMiningConstraint(Block.MaxTransactionsPerBlockVer3, TxEstimators.one)))
```
