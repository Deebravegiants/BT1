# [?] Fix loadgen non-determinism and regenerate tx meta.

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2023-12-22
Source: https://github.com/stellar/stellar-core/commit/8f5242e34d570714a32714aab3c3e755f13fe1d5
Type: security-commit

## Details
Fix loadgen non-determinism and regenerate tx meta.

## Patch
### src/simulation/LoadGenerator.cpp
```diff
@@ -1239,7 +1239,11 @@ LoadGenerator::createContractTransaction(uint32_t ledgerNum, uint64_t accountId,
     createResources.readBytes = mContactOverheadBytes;
     createResources.writeBytes = 300;
 
-    auto salt = sha256(std::to_string(mContractInstanceKeys.size()));
+    auto salt = sha256(
+        std::to_string(mContractInstanceKeys.size()) + "run" +
+        std::to_string(mApp.getMetrics()
+                           .NewMeter({"loadgen", "run", "complete"}, "run")
+                           .count()));
     auto contractIDPreimage = makeContractIDPreimage(*account, salt);
 
     auto tx =
```

### test-tx-meta-baseline-current/InvokeHostFunctionTests.json
```diff
@@ -470,8 +470,21 @@
 		"bKDF6V5IzTo="
 	],
 	"contract storage|footprint|unused readWrite key" : [ "ZKxMUP1fxqo=" ],
-	"failure diagnostics" : [ "bKDF6V5IzTo=", "bKDF6V5IzTo=" ],
+	"failure diagnostics" : [ "bKDF6V5IzTo=" ],
 	"ledger entry size limit enforced" : [ "bKDF6V5IzTo=", "bKDF6V5IzTo=" ],
+	"loadgen Wasm executes properly" : [ "bKDF6V5IzTo=" ],
+	"overly large soroban values are handled gracefully" : 
+	[
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo="
+	],
 	"refund account merged" : [ "bKDF6V5IzTo=", "y0mODi4DFnM=", "o9mb+GfjtK8=", "HG7OrQT/Ofg=" ],
 	"settings upgrade" : [ "bKDF6V5IzTo=", "bKDF6V5IzTo=" ],
 	"settings upgrade command line utils" : [ "TByXElZpITE=", "TByXElZpITE=", "TByXElZpITE=", "TByXElZpITE=" ],
@@ -505,5 +518,6 @@
 		"bKDF6V5IzTo=",
 		"bKDF6V5IzTo="
 	],
-	"temp entry eviction" : [ "bKDF6V5IzTo=", "bKDF6V5IzTo=" ]
+	"temp entry eviction" : [ "bKDF6V5IzTo=", "bKDF6V5IzTo=" ],
+	"transaction validation diagnostics" : [ "bKDF6V5IzTo=" ]
 }
```

### test-tx-meta-baseline-next/InvokeHostFunctionTests.json
```diff
@@ -471,8 +471,21 @@
 		"bKDF6V5IzTo="
 	],
 	"contract storage|footprint|unused readWrite key" : [ "ZKxMUP1fxqo=" ],
-	"failure diagnostics" : [ "bKDF6V5IzTo=", "bKDF6V5IzTo=" ],
+	"failure diagnostics" : [ "bKDF6V5IzTo=" ],
 	"ledger entry size limit enforced" : [ "bKDF6V5IzTo=", "bKDF6V5IzTo=" ],
+	"loadgen Wasm executes properly" : [ "bKDF6V5IzTo=" ],
+	"overly large soroban values are handled gracefully" : 
+	[
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo=",
+		"bKDF6V5IzTo="
+	],
 	"refund account merged" : [ "bKDF6V5IzTo=", "y0mODi4DFnM=", "o9mb+GfjtK8=", "HG7OrQT/Ofg=" ],
 	"settings upgrade" : [ "bKDF6V5IzTo=", "bKDF6V5IzTo=" ],
 	"settings upgrade command line utils" : [ "TByXElZpITE=", "TByXElZpITE=", "TByXElZpITE=", "TByXElZpITE=" ],
@@ -506,5 +519,6 @@
 		"bKDF6V5IzTo=",
 		"bKDF6V5IzTo="
 	],
-	"temp entry eviction" : [ "bKDF6V5IzTo=", "bKDF6V5IzTo=" ]
+	"temp entry eviction" : [ "bKDF6V5IzTo=", "bKDF6V5IzTo=" ],
+	"transaction validation diagnostics" : [ "bKDF6V5IzTo=" ]
 }
```
