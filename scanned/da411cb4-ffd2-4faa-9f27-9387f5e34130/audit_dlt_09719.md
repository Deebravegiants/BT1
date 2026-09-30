# [?] audit fix: L-02 => Non-Idempotent CREATE2 Deploy Can DoS Deployment Script

## Summary
Severity: Unknown
Chain: EtherFi
Component: etherfi-protocol/smart-contracts
Published: 2026-02-18
Source: https://github.com/etherfi-protocol/smart-contracts/commit/3e614129efbafd7308951eb0048dbeefbfee6039
Type: security-commit

## Details
audit fix: L-02 => Non-Idempotent CREATE2 Deploy Can DoS Deployment Script

## Patch
### script/utils/utils.sol
```diff
@@ -32,12 +32,24 @@ contract Utils is Script, Deployed {
     uint256 constant MIN_DELAY_TIMELOCK = 259200; // 72 hours
 
     function deploy(string memory contractName, bytes memory constructorArgs, bytes memory bytecode, bytes32 salt, bool logging, ICreate2Factory factory) internal returns (address) {
-        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
         address predictedAddress = factory.computeAddress(salt, bytecode);
-        address deployedAddress = factory.deploy(bytecode, salt);
-        require(deployedAddress == predictedAddress, "Deployment address mismatch");
+        bool alreadyDeployed = predictedAddress.code.length > 0;
+        address deployedAddress = predictedAddress;
+
+        if (alreadyDeployed) {
+            // Idempotent path: script reruns should reuse the existing deployment.
+            require(factory.verify(predictedAddress, salt, bytecode), "Existing code at predicted address does not match");
+        } else {
+            deployedAddress = factory.deploy(bytecode, salt);
+            require(deployedAddress == predictedAddress, "Deployment address mismatch");
+        }
 
         if (logging) {
+            if (alreadyDeployed) {
+                console.log("\n=== Deployment Skipped (Already Deployed) ===");
+                console.log("Contract:", contractName);
+                console.log("Address:", predictedAddress);
+            }
 
             // 5. Create JSON deployment log (exact same format)
             string memory deployLog = string.concat(
```
