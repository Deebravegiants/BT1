# [?] fix: improve error handling and code clarity in overflow_test.ts (#711)

## Summary
Severity: Unknown
Chain: Morph
Component: morph-l2/morph
Published: 2025-02-08
Source: https://github.com/morph-l2/morph/commit/f4698e42295aae56aa241ac420bd8c22b6f79135
Type: security-commit

## Details
fix: improve error handling and code clarity in overflow_test.ts (#711)

## Patch
### contracts/tasks/overflow_test.ts
```diff
@@ -81,39 +81,57 @@ task("crossHash")
     .addParam("message")
     .addParam("count")
     .setAction(async (taskArgs, hre) => {
-        const addr = taskArgs.contractaddr
-        const message = taskArgs.message
-        const count = taskArgs.count
-
-        const deployer = await hre.ethers.provider.getSigner();
-        const MyContract = await hre.ethers.getContractFactory("L1OverflowTester", deployer);
-        const contract = MyContract.attach(addr);
-
-        console.log("sending tx for crossHash......")
-        //const options = {value: ethers.utils.parseEther("1.0")}
-        const txn = await contract["crossHash(string,uint256)"](message, count, { value: ethers.utils.parseEther("0.002") })
-
-        //let txn = await contract.crossHash(message, count, options)
-        await txn.wait();
-        console.log(txn)
-
-    })
+        try {
+            const addr = taskArgs.contractaddr;
+            const message = taskArgs.message;
+            const count = taskArgs.count;
+
+            const deployer = await hre.ethers.provider.getSigner();
+            const MyContract = await hre.ethers.getContractFactory("L1OverflowTester", deployer);
+            const contract = MyContract.attach(addr);
+
+            console.log("Sending transaction for crossHash...");
+            const txn = await contract["crossHash(string,uint256)"](message, count, { 
+                value: ethers.utils.parseEther("0.002") 
+            });
+
+            const receipt = await txn.wait();
+            console.log("Transaction successful:", {
+                hash: txn.hash,
+                blockNumber: receipt.blockNumber,
+                status: receipt.status === 1 ? 'Success' : 'Failed'
+            });
+        } catch (error) {
+            console.error("Error in crossHash task:", error.message);
+            throw error;
+        }
+    });
 
 task("updateLimit")
     .addParam("contractaddr")
     .addParam("gaslimit")
     .setAction(async (taskArgs, hre) => {
-        const addr = taskArgs.contractaddr
-        const gasLimit = taskArgs.gaslimit
-        const deployer = await hre.ethers.provider.getSigner();
-        const MyContract = await hre.ethers.getContractFactory("L1OverflowTester", deployer);
-        const contract = MyContract.attach(addr);
-
-        console.log("sending tx for updateGasLimit......");
-        let txn = await contract.updateGasLimit(gasLimit);
-        await txn.wait();
-        console.log(txn);
-    })
+        try {
+            const addr = taskArgs.contractaddr;
+            const gasLimit = taskArgs.gaslimit;
+            const deployer = await hre.ethers.provider.getSigner();
+            const MyContract = await hre.ethers.getContractFactory("L1OverflowTester", deployer);
+            const contract = MyContract.attach(addr);
+
+            console.log("Sending transaction for updateGasLimit...");
+            const txn = await contract.updateGasLimit(gasLimit);
+            const receipt = await txn.wait();
+            
+            console.log("Transaction successful:", {
+                hash: txn.hash,
+                blockNumber: receipt.blockNumber,
+                status: receipt.status === 1 ? 'Success' : 'Failed'
+            });
+        } catch (error) {
+            console.error("Error in updateLimit task:", error.message);
+            throw error;
+        }
+    });
 
 task("printResult")
     .addParam("contractaddr")
```
