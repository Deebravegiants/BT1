# [?] fix(op-hardforks): fix `ethereum_fork_activation` panic on Bpo*/Amsterdam hardforks (alloy-rs/hardforks#64)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2025-09-16
Source: https://github.com/ethereum-optimism/optimism/commit/adf129993e0eeab677a07a3552ef83e945f95f78
Type: security-commit

## Details
fix(op-hardforks): fix `ethereum_fork_activation` panic on Bpo*/Amsterdam hardforks (alloy-rs/hardforks#64)

## Patch
### src/lib.rs
```diff
@@ -279,7 +279,9 @@ impl OpChainHardforks {
 
 impl EthereumHardforks for OpChainHardforks {
     fn ethereum_fork_activation(&self, fork: EthereumHardfork) -> ForkCondition {
-        use EthereumHardfork::{Cancun, Osaka, Prague, Shanghai};
+        use EthereumHardfork::{
+            Amsterdam, Bpo1, Bpo2, Bpo3, Bpo4, Bpo5, Cancun, Osaka, Prague, Shanghai,
+        };
         use OpHardfork::{Canyon, Ecotone, Isthmus};
 
         if self.forks.is_empty() {
@@ -292,7 +294,7 @@ impl EthereumHardforks for OpChainHardforks {
             Shanghai if forks_len <= Canyon.idx() => ForkCondition::Never,
             Cancun if forks_len <= Ecotone.idx() => ForkCondition::Never,
             Prague if forks_len <= Isthmus.idx() => ForkCondition::Never,
-            Osaka => ForkCondition::Never,
+            Osaka | Bpo1 | Bpo2 | Bpo3 | Bpo4 | Bpo5 | Amsterdam => ForkCondition::Never,
             _ => self[fork],
         }
     }
@@ -562,4 +564,16 @@ mod tests {
         // Edge cases
         assert_eq!(OpHardfork::from_chain_and_timestamp(Chain::from_id(999999), 1000000), None);
     }
+
+    // https://github.com/alloy-rs/hardforks/issues/63
+    #[test]
+    fn test_ethereum_fork_activation_consistency() {
+        let op_mainnet_forks = OpChainHardforks::op_mainnet();
+        for ethereum_hardfork in EthereumHardfork::VARIANTS {
+            let _ = op_mainnet_forks.ethereum_fork_activation(*ethereum_hardfork);
+        }
+        for op_hardfork in OpHardfork::VARIANTS {
+            let _ = op_mainnet_forks.op_fork_activation(*op_hardfork);
+        }
+    }
 }
```
