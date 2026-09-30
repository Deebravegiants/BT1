# [?] Resolve potential reentrancy situations

## Summary
Severity: Unknown
Chain: Rocket Pool
Component: rocket-pool/rocketpool
Published: 2021-06-22
Source: https://github.com/rocket-pool/rocketpool/commit/22266af9f19ffb7a3f904548513cc2f31490c193
Type: security-commit

## Details
Resolve potential reentrancy situations

## Patch
### contracts/contract/minipool/RocketMinipoolDelegate.sol
```diff
@@ -147,12 +147,12 @@ contract RocketMinipoolDelegate is RocketMinipoolStorageLayout, RocketMinipoolIn
         require(address(this).balance >= launchAmount, "Insufficient balance to begin staking");
         // Check validator pubkey is not in use
         require(rocketMinipoolManager.getMinipoolByPubkey(_validatorPubkey) == address(0x0), "Validator pubkey is already in use");
-        // Send staking deposit to casper
-        casperDeposit.deposit{value: launchAmount}(_validatorPubkey, getWithdrawalCredentials(), _validatorSignature, _depositDataRoot);
         // Set minipool pubkey
         rocketMinipoolManager.setMinipoolPubkey(_validatorPubkey);
         // Progress to staking
         setStatus(MinipoolStatus.Staking);
+        // Send staking deposit to casper
+        casperDeposit.deposit{value: launchAmount}(_validatorPubkey, getWithdrawalCredentials(), _validatorSignature, _depositDataRoot);
     }
 
     // Mark the minipool as withdrawable and record its final balance
@@ -211,20 +211,22 @@ contract RocketMinipoolDelegate is RocketMinipoolStorageLayout, RocketMinipoolIn
             (status == MinipoolStatus.Prelaunch && block.number.sub(statusBlock) >= rocketDAOProtocolSettingsMinipool.getLaunchTimeout()),
             "The minipool can only be dissolved by its owner unless it has timed out"
         );
+        // Progress to dissolved
+        setStatus(MinipoolStatus.Dissolved);
         // Transfer user balance to deposit pool
         if (userDepositBalance > 0) {
-            // Transfer 
-            rocketDepositPool.recycleDissolvedDeposit{value: userDepositBalance}();
-            // Emit ether withdrawn event
-            emit EtherWithdrawn(address(rocketDepositPool), userDepositBalance, block.timestamp);
+            // Store value in local
+            uint256 recycleAmount = userDepositBalance;
             // Clear storage
             userDepositBalance = 0;
             userDepositAssignedTime = 0;
+            // Transfer
+            rocketDepositPool.recycleDissolvedDeposit{value: recycleAmount}();
+            // Emit ether withdrawn event
+            emit EtherWithdrawn(address(rocketDepositPool), recycleAmount, block.timestamp);
         } else {
             rocketMinipoolQueue.removeMinipool(depositType);
         }
-        // Progress to dissolved
-        setStatus(MinipoolStatus.Dissolved);
     }
 
     // Withdraw node balances from the minipool and close it
```
