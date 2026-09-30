# [?] 9559 Increased timeout in the assertions to prevent non-deterministic failures. (#9560)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2023-11-01
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/3747a575db6c3b8df100dbe3164b1396b107e9ce
Type: security-commit

## Details
9559 Increased timeout in the assertions to prevent non-deterministic failures. (#9560)

Signed-off-by: Ivan Malygin <ivan@swirldslabs.com>

## Patch
### platform-sdk/swirlds-jasperdb/src/test/java/com/swirlds/merkledb/MerkleDbCompactionCoordinatorTest.java
```diff
@@ -293,7 +293,7 @@ private void testCompactionFailed(DataFileCompactor compactorToTest, Runnable me
                     }
                     verifyNoInteractions(statisticsUpdater);
                 },
-                Duration.ofMillis(100),
+                Duration.ofSeconds(1),
                 "Unexpected mock state");
     }
 
@@ -325,7 +325,7 @@ private void assertCompactable(DataFileCompactor compactorToTest, boolean expect
                         throw new RuntimeException(e);
                     }
                 },
-                Duration.ofMillis(100),
+                Duration.ofSeconds(1),
                 "Unexpected mock state");
     }
 }
```
