# [?] Fix for underflow error when offchain price timestamp is bigger than current block timestamp (#2195)

## Summary
Severity: Unknown
Chain: Synthetix
Component: Synthetixio/synthetix-v3
Published: 2024-07-13
Source: https://github.com/Synthetixio/synthetix-v3/commit/2ac0fdfed5ff1ec687da9903d8fdc54394dada89
Type: security-commit

## Details
Fix for underflow error when offchain price timestamp is bigger than current block timestamp (#2195)

* Fix for underflow error when offchain price timestamp is bigger than current block timestamp

* Add a test for the price update from the future

* Simplified staleness check

## Patch
### protocol/oracle-manager/contracts/nodes/StalenessCircuitBreakerNode.sol
```diff
@@ -31,7 +31,7 @@ library StalenessCircuitBreakerNode {
             runtimeValues
         );
 
-        if (block.timestamp - priceNodeOutput.timestamp <= stalenessTolerance) {
+        if (block.timestamp - stalenessTolerance <= priceNodeOutput.timestamp) {
             return priceNodeOutput;
         } else if (nodeDefinition.parents.length == 1) {
             revert StalenessToleranceExceeded(
```

### protocol/oracle-manager/test/integration/nodes/StalenessCircuitBreakerNode.test.ts
```diff
@@ -10,6 +10,7 @@ describe('StalenessCircuitBreakerNode', function () {
   const { getContract, getSigners, getProvider } = bootstrap();
   let owner: Signer;
   let staleNodeId: string;
+  let futureNodeId: string;
   let freshNodeId: string;
   let fallbackNodeId: string;
   let zeroPriceNodeId: string;
@@ -25,6 +26,7 @@ describe('StalenessCircuitBreakerNode', function () {
 
     const currentTimestamp = (await getProvider().getBlock('latest')).timestamp;
     staleNodeId = await deployAndRegisterExternalNode(100, currentTimestamp - 100);
+    futureNodeId = await deployAndRegisterExternalNode(69, currentTimestamp + 100);
     freshNodeId = await deployAndRegisterExternalNode(200, currentTimestamp - 10);
     fallbackNodeId = await deployAndRegisterExternalNode(300, currentTimestamp);
     zeroPriceNodeId = await deployAndRegisterExternalNode(0, currentTimestamp);
@@ -101,6 +103,19 @@ describe('StalenessCircuitBreakerNode', function () {
     );
   });
 
+  it('allows price update from the future', async () => {
+    // Register staleness circuit breaker node with stale parent
+    const NodeParameters = abi.encode(['uint'], [stalenessTolerance]);
+    await NodeModule.registerNode(NodeTypes.STALENESS_CIRCUIT_BREAKER, NodeParameters, [
+      futureNodeId,
+    ]);
+    const nodeId = await NodeModule.getNodeId(NodeTypes.STALENESS_CIRCUIT_BREAKER, NodeParameters, [
+      futureNodeId,
+    ]);
+    const nodeOutput = await NodeModule.process(nodeId);
+    assertBn.equal(69, nodeOutput.price);
+  });
+
   async function deployAndRegisterExternalNode(price: BigNumberish, timestamp: BigNumberish) {
     // Deploy the mock
     const factory = await hre.ethers.getContractFactory('MockExternalNode');
```
