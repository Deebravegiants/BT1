# [?] KS-391: Capabilities registry reentrancy fix (#13970)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2024-08-09
Source: https://github.com/smartcontractkit/chainlink/commit/cefbb09797249309ac18e4ef81147e30f7c24360
Type: security-commit

## Details
KS-391: Capabilities registry reentrancy fix (#13970)

* prevent malicious a node operator from taking over another node belonging to another node operator

* prevent malicious node operator from becoming the admin for another node operator

* prevent reentrancy when setting DON config

* update wrappers and add changeset

* fix solhint

## Patch
### .changeset/weak-rabbits-sell.md
```diff
@@ -0,0 +1,5 @@
+---
+"chainlink": patch
+---
+
+#internal prevent reentrancy when configuring DON in Capabilities Registry
```

### contracts/.changeset/tender-comics-check.md
```diff
@@ -0,0 +1,5 @@
+---
+'@chainlink/contracts': patch
+---
+
+#internal prevent reentrancy when configuring DON in capabilities registry
```

### contracts/src/v0.8/keystone/CapabilitiesRegistry.sol
```diff
@@ -961,6 +961,11 @@ contract CapabilitiesRegistry is OwnerIsCreator, TypeAndVersionInterface {
       donCapabilityConfig.capabilityIds.push(configuration.capabilityId);
       donCapabilityConfig.capabilityConfigs[configuration.capabilityId] = configuration.config;
 
+      s_dons[donParams.id].isPublic = donParams.isPublic;
+      s_dons[donParams.id].acceptsWorkflows = donParams.acceptsWorkflows;
+      s_dons[donParams.id].f = donParams.f;
+      s_dons[donParams.id].configCount = donParams.configCount;
+
       _setDONCapabilityConfig(
         donParams.id,
         donParams.configCount,
@@ -969,10 +974,6 @@ contract CapabilitiesRegistry is OwnerIsCreator, TypeAndVersionInterface {
         configuration.config
       );
     }
-    s_dons[donParams.id].isPublic = donParams.isPublic;
-    s_dons[donParams.id].acceptsWorkflows = donParams.acceptsWorkflows;
-    s_dons[donParams.id].f = donParams.f;
-    s_dons[donParams.id].configCount = donParams.configCount;
     emit ConfigSet(donParams.id, donParams.configCount);
   }
 
```

### contracts/src/v0.8/keystone/test/CapabilitiesRegistry_AddDONTest.t.sol
```diff
@@ -4,6 +4,7 @@ pragma solidity 0.8.24;
 import {BaseTest} from "./BaseTest.t.sol";
 import {ICapabilityConfiguration} from "../interfaces/ICapabilityConfiguration.sol";
 import {CapabilitiesRegistry} from "../CapabilitiesRegistry.sol";
+import {MaliciousConfigurationContract} from "./mocks/MaliciousConfigurationContract.sol";
 
 contract CapabilitiesRegistry_AddDONTest is BaseTest {
   function setUp() public override {
@@ -245,3 +246,75 @@ contract CapabilitiesRegistry_AddDONTest is BaseTest {
     assertEq(donInfo.nodeP2PIds[1], P2P_ID_THREE);
   }
 }
+
+contract CapabilitiesRegistry_AddDONTest_WhenMaliciousCapabilityConfigurationConfigured is BaseTest {
+  function setUp() public override {
+    BaseTest.setUp();
+    CapabilitiesRegistry.Capability[] memory capabilities = new CapabilitiesRegistry.Capability[](2);
+
+    address maliciousConfigContractAddr = address(
+      new MaliciousConfigurationContract(s_capabilityWithConfigurationContractId)
+    );
+    s_basicCapability.configurationContract = maliciousConfigContractAddr;
+    capabilities[0] = s_basicCapability;
+    capabilities[1] = s_capabilityWithConfigurationContract;
+
+    CapabilitiesRegistry.NodeOperator[] memory nodeOperators = _getNodeOperators();
+    nodeOperators[0].admin = maliciousConfigContractAddr;
+    nodeOperators[1].admin = maliciousConfigContractAddr;
+    nodeOperators[2].admin = maliciousConfigContractAddr;
+
+    s_CapabilitiesRegistry.addNodeOperators(nodeOperators);
+    s_CapabilitiesRegistry.addCapabilities(capabilities);
+
+    CapabilitiesRegistry.NodeParams[] memory nodes = new CapabilitiesRegistry.NodeParams[](3);
+    bytes32[] memory capabilityIds = new bytes32[](1);
+    capabilityIds[0] = s_basicHashedCapabilityId;
+
+    nodes[0] = CapabilitiesRegistry.NodeParams({
+      nodeOperatorId: TEST_NODE_OPERATOR_ONE_ID,
+      p2pId: P2P_ID,
+      signer: NODE_OPERATOR_ONE_SIGNER_ADDRESS,
+      hashedCapabilityIds: capabilityIds
+    });
+
+    bytes32[] memory nodeTwoCapabilityIds = new bytes32[](1);
+    nodeTwoCapabilityIds[0] = s_basicHashedCapabilityId;
+
+    nodes[1] = CapabilitiesRegistry.NodeParams({
+      nodeOperatorId: TEST_NODE_OPERATOR_TWO_ID,
+      p2pId: P2P_ID_TWO,
+      signer: NODE_OPERATOR_TWO_SIGNER_ADDRESS,
+      hashedCapabilityIds: nodeTwoCapabilityIds
+    });
+
+    nodes[2] = CapabilitiesRegistry.NodeParams({
+      nodeOperatorId: TEST_NODE_OPERATOR_THREE_ID,
+      p2pId: P2P_ID_THREE,
+      signer: NODE_OPERATOR_THREE_SIGNER_ADDRESS,
+      hashedCapabilityIds: capabilityIds
+    });
+
+    s_CapabilitiesRegistry.addNodes(nodes);
+
+    changePrank(ADMIN);
+  }
+
+  function test_RevertWhen_MaliciousCapabilitiesConfigContractTriesToRemoveCapabilitiesFromDONNodes() public {
+    bytes32[] memory nodes = new bytes32[](2);
+    nodes[0] = P2P_ID;
+    nodes[1] = P2P_ID_THREE;
+
+    CapabilitiesRegistry.CapabilityConfiguration[]
+      memory capabilityConfigs = new CapabilitiesRegistry.CapabilityConfiguration[](1);
+    capabilityConfigs[0] = CapabilitiesRegistry.CapabilityConfiguration({
+      capabilityId: s_basicHashedCapabilityId,
+      config: BASIC_CAPABILITY_CONFIG
+    });
+
+    vm.expectRevert(
+      abi.encodeWithSelector(CapabilitiesRegistry.CapabilityRequiredByDON.selector, s_basicHashedCapabilityId, DON_ID)
+    );
+    s_CapabilitiesRegistry.addDON(nodes, capabilityConfigs, true, true, F_VALUE);
+  }
+}
```

### contracts/src/v0.8/keystone/test/mocks/MaliciousConfigurationContract.sol
```diff
@@ -0,0 +1,47 @@
+// SPDX-License-Identifier: MIT
+pragma solidity 0.8.24;
+
+import {ICapabilityConfiguration} from "../../interfaces/ICapabilityConfiguration.sol";
+import {CapabilitiesRegistry} from "../../CapabilitiesRegistry.sol";
+import {ERC165} from "../../../vendor/openzeppelin-solidity/v4.8.3/contracts/utils/introspection/ERC165.sol";
+import {Constants} from "../Constants.t.sol";
+
+contract MaliciousConfigurationContract is ICapabilityConfiguration, ERC165, Constants {
+  bytes32 internal s_capabilityWithConfigurationContractId;
+
+  constructor(bytes32 capabilityWithConfigContractId) {
+    s_capabilityWithConfigurationContractId = capabilityWithConfigContractId;
+  }
+
+  function getCapabilityConfiguration(uint32) external view returns (bytes memory configuration) {
+    return bytes("");
+  }
+
+  function beforeCapabilityConfigSet(bytes32[] calldata, bytes calldata, uint64, uint32) external {
+    CapabilitiesRegistry.NodeParams[] memory nodes = new CapabilitiesRegistry.NodeParams[](2);
+    bytes32[] memory hashedCapabilityIds = new bytes32[](1);
+
+    hashedCapabilityIds[0] = s_capabilityWithConfigurationContractId;
+
+    // Set node one's signer to another address
+    nodes[0] = CapabilitiesRegistry.NodeParams({
+      nodeOperatorId: TEST_NODE_OPERATOR_ONE_ID,
+      p2pId: P2P_ID,
+      signer: NODE_OPERATOR_ONE_SIGNER_ADDRESS,
+      hashedCapabilityIds: hashedCapabilityIds
+    });
+
+    nodes[1] = CapabilitiesRegistry.NodeParams({
+      nodeOperatorId: TEST_NODE_OPERATOR_ONE_ID,
+      p2pId: P2P_ID_THREE,
+      signer: NODE_OPERATOR_THREE_SIGNER_ADDRESS,
+      hashedCapabilityIds: hashedCapabilityIds
+    });
+
+    CapabilitiesRegistry(msg.sender).updateNodes(nodes);
+  }
+
+  function supportsInterface(bytes4 interfaceId) public pure override returns (bool) {
+    return interfaceId == this.getCapabilityConfiguration.selector ^ this.beforeCapabilityConfigSet.selector;
+  }
+}
```

### core/gethwrappers/keystone/generation/generated-wrapper-dependency-versions-do-not-edit.txt
```diff
@@ -1,5 +1,5 @@
 GETH_VERSION: 1.13.8
-capabilities_registry: ../../../contracts/solc/v0.8.24/CapabilitiesRegistry/CapabilitiesRegistry.abi ../../../contracts/solc/v0.8.24/CapabilitiesRegistry/CapabilitiesRegistry.bin 6d2e3aa3a6f3aed2cf24b613743bb9ae4b9558f48a6864dc03b8b0ebb37235e3
+capabilities_registry: ../../../contracts/solc/v0.8.24/CapabilitiesRegistry/CapabilitiesRegistry.abi ../../../contracts/solc/v0.8.24/CapabilitiesRegistry/CapabilitiesRegistry.bin bb794cc0042784b060d1d63090e2086670b88ba3685067cd436305f36054c82b
 feeds_consumer: ../../../contracts/solc/v0.8.24/KeystoneFeedsConsumer/KeystoneFeedsConsumer.abi ../../../contracts/solc/v0.8.24/KeystoneFeedsConsumer/KeystoneFeedsConsumer.bin 8c3a2b18a80be41e7c40d2bc3a4c8d1b5e18d55c1fd20ad5af68cebb66109fc5
 forwarder: ../../../contracts/solc/v0.8.24/KeystoneForwarder/KeystoneForwarder.abi ../../../contracts/solc/v0.8.24/KeystoneForwarder/KeystoneForwarder.bin 45d9b866c64b41c1349a90b6764aee42a6d078b454d38f369b5fe02b23b9d16e
 ocr3_capability: ../../../contracts/solc/v0.8.24/OCR3Capability/OCR3Capability.abi ../../../contracts/solc/v0.8.24/OCR3Capability/OCR3Capability.bin 8bf0f53f222efce7143dea6134552eb26ea1eef845407b4475a0d79b7d7ba9f8
```
