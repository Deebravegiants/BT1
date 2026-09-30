# [?] Prevent underflow in newValidator when underbonded by > 32 ETH

## Summary
Severity: Unknown
Chain: Rocket Pool
Component: rocket-pool/rocketpool
Published: 2026-01-16
Source: https://github.com/rocket-pool/rocketpool/commit/3975a26fe2e5ee8c1f75ed5c0931d394a8ca7cd6
Type: security-commit

## Details
Prevent underflow in newValidator when underbonded by > 32 ETH

## Patch
### contracts/contract/megapool/RocketMegapoolDelegate.sol
```diff
@@ -173,10 +173,15 @@ contract RocketMegapoolDelegate is RocketMegapoolDelegateBase, RocketMegapoolDel
         uint256 newBondRequirement = rocketNodeDeposit.getBondRequirement(getActiveValidatorCount() + 1);
         uint256 effectiveBond = nodeBond + nodeQueuedBond;
         if (newBondRequirement > effectiveBond) {
+            // Clamp new bond requirement between 1 - 32 ETH
             if (newBondRequirement - effectiveBond < prestakeValue) {
                 return prestakeValue;
             } else {
-                return newBondRequirement - effectiveBond;
+                uint256 bondRequirement = newBondRequirement - effectiveBond;
+                if (bondRequirement > fullDepositValue) {
+                    bondRequirement = fullDepositValue;
+                }
+                return bondRequirement;
             }
         } else {
             return prestakeValue;
```

### test/dao/dao-node-trusted-tests.js
```diff
@@ -1,4 +1,4 @@
-import { describe, it, before } from 'mocha';
+import { before, describe, it } from 'mocha';
 import { printTitle } from '../_utils/formatting';
 import { shouldRevert } from '../_utils/testing';
 import { compressABI } from '../_utils/contract';
@@ -34,11 +34,14 @@ import {
 import { assertBN } from '../_helpers/bn';
 import {
     RocketDAONodeTrusted,
-    RocketDAONodeTrustedActions, RocketDAONodeTrustedProposals,
+    RocketDAONodeTrustedActions,
+    RocketDAONodeTrustedProposals,
     RocketDAONodeTrustedSettingsMembers,
     RocketDAONodeTrustedSettingsProposals,
     RocketDAONodeTrustedUpgrade,
-    RocketDAOProtocolSettingsMegapool, RocketDAOProtocolSettingsNode, RocketDAOProtocolSettingsSecurity,
+    RocketDAOProtocolSettingsMegapool,
+    RocketDAOProtocolSettingsNode,
+    RocketDAOProtocolSettingsSecurity,
     RocketMinipoolManager,
     RocketStorage,
     RocketTokenRPL,
@@ -853,8 +856,8 @@ export default function() {
             const address = await rocketDAONodeTrustedUpgrade.getUpgradeAddress(1n);
             const expectedType = ethers.solidityPackedKeccak256(['string'], ['upgradeContract']);
             assert.equal(address, rocketMinipoolManagerNew.target);
-            assert.equal(type, expectedType)
-            assert.equal(name, 'rocketNodeManager')
+            assert.equal(type, expectedType);
+            assert.equal(name, 'rocketNodeManager');
             // Upgrade should fail before delay
             await shouldRevert(
                 rocketDAONodeTrustedUpgrade.connect(registeredNodeTrusted1).execute(1n),
@@ -966,22 +969,22 @@ export default function() {
         });
 
         it(printTitle('guardian', 'can not set "reduced.bond" to a value not divisible by milliwei'), async () => {
-            // Can set to 1 ether + 1 milliwei
-            await setDAOProtocolBootstrapSetting(RocketDAOProtocolSettingsNode, 'reduced.bond', 1001000000000000000n, { from: guardian });
+            // Can set to 2 ether + 1 milliwei
+            await setDAOProtocolBootstrapSetting(RocketDAOProtocolSettingsNode, 'reduced.bond', 2001000000000000000n, { from: guardian });
             // Cannot set to 1 ether + 1 milliwei + 1 microwei
             await shouldRevert(
                 setDAOProtocolBootstrapSetting(RocketDAOProtocolSettingsNode, 'reduced.bond', 1001001000000000000n, { from: guardian }),
                 'Was able to set "reduced.bond" to value not divisible by milliwei',
-                'Value must be divisible by milliwei'
-            )
+                'Value must be divisible by milliwei',
+            );
         });
 
         it(printTitle('guardian', 'can not set "megapool.dissolve.penalty" to zero'), async () => {
             await shouldRevert(
                 setDAOProtocolBootstrapSetting(RocketDAOProtocolSettingsMegapool, 'megapool.dissolve.penalty', 0n, { from: guardian }),
                 'Was able to set "megapool.dissolve.penalty" to zero',
-                'Value must be >= 0.01 ETH'
-            )
+                'Value must be >= 0.01 ETH',
+            );
         });
 
         it(printTitle('guardian', 'can add a contract ABI in bootstrap mode'), async () => {
```

### test/megapool/megapool-tests.js
```diff
@@ -994,6 +994,44 @@ export default function() {
             await nodeDeposit(node, '8'.ether);
         });
 
+        it(printTitle('node', 'can create a new validator if bond requirement increases and node is underbonded by > 32 ETH'), async () => {
+            const dissolvePeriod = (60 * 60 * 24 * 10); // 10 Days
+            await setDAOProtocolBootstrapSetting(RocketDAOProtocolSettingsMegapool, 'megapool.time.before.dissolve', dissolvePeriod, { from: owner });
+            // Reduce reduced.bond to 2 ETH
+            await setDAOProtocolBootstrapSetting(RocketDAOProtocolSettingsNode, 'reduced.bond', '2'.ether, { from: owner });
+            // Increase deposit pool capacity
+            await setDAOProtocolBootstrapSetting(RocketDAOProtocolSettingsDeposit, 'deposit.pool.maximum', '10000'.ether, { from: owner });
+            // Set penalty to 0.1 ETH
+            const dissolvePenalty = '0.1'.ether;
+            await setDAOProtocolBootstrapSetting(RocketDAOProtocolSettingsMegapool, 'megapool.dissolve.penalty', dissolvePenalty, { from: owner });
+            // Deposit ETH
+            await userDeposit({ from: random, value: '30'.ether * 35n });
+            // Make 32 validators with 2 ETH bond
+            await nodeDeposit(node, '4'.ether);
+            await nodeDeposit(node, '4'.ether);
+            for (let i = 0n; i < 30n; i++) {
+                await nodeDeposit(node, '2'.ether);
+            }
+            // Node should now have 32 active validators with a bond of 4+4+(2*30) = 68ETH
+            assertBN.equal(await megapool.getNodeBond(), '68'.ether);
+            assertBN.equal(await megapool.getUserCapital(), '32'.ether * 32n - '68'.ether);
+            assertBN.equal(await megapool.getNodeQueuedBond(), '0'.ether);
+            assertBN.equal(await megapool.getUserQueuedCapital(), '0'.ether);
+            // Increase reduced.bond back to 4 ETH
+            await setDAOProtocolBootstrapSetting(RocketDAOProtocolSettingsNode, 'reduced.bond', '4'.ether, { from: owner });
+            // Node is now underbonded by 4+4+(4*30)-68 = 60 ETH so next validator must have 32 ETH bond
+            assertBN.equal(await megapool.getNewValidatorBondRequirement(), '32'.ether);
+            await nodeDeposit(node, '32'.ether);
+            // Node now has bond of 68+32 = 100, bond requirement with new validator is is 4+4+(4*32) = 136 ETH, so next validator requires 32 ETH
+            assertBN.equal(await megapool.getNodeBond(), '100'.ether);
+            assertBN.equal(await megapool.getNewValidatorBondRequirement(), '32'.ether);
+            await nodeDeposit(node, '32'.ether);
+            // Node now has bond of 100 + 32 = 132, bond requirement with new validator is 4+4+(4*33) = 140 ETH, so next validator requires 8 ETH
+            assertBN.equal(await megapool.getNodeBond(), '132'.ether);
+            assertBN.equal(await megapool.getNewValidatorBondRequirement(), '8'.ether);
+            await nodeDeposit(node, '8'.ether);
+        });
+
         it(printTitle('node', 'can dissolve and exit validators when underbonded'), async () => {
             const dissolvePeriod = (60 * 60 * 24 * 10); // 10 Days
             await setDAOProtocolBootstrapSetting(RocketDAOProtocolSettingsMegapool, 'megapool.time.before.dissolve', dissolvePeriod, { from: owner });
@@ -1074,7 +1112,8 @@ export default function() {
             }
             assertBN.equal(await megapool.getNodeBond(), '0'.ether);
             assertBN.equal(await megapool.getUserCapital(), '0'.ether);
-        });
+        })
+
 
         it(printTitle('node', 'cannot exit queue to underbonded state due to dissolves'), async () => {
             const dissolvePeriod = (60 * 60 * 24 * 10); // 10 Days
```
