# [?] add reentrancy guard (#12447)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2024-03-19
Source: https://github.com/smartcontractkit/ccip/commit/ee06eb28fb27541ca81f072ff306ea0f85fa0b35
Type: security-commit

## Details
add reentrancy guard (#12447)

Signed-off-by: Borja Aranda <borja.aranda@smartcontract.com>

## Patch
### contracts/src/v0.8/automation/upkeeps/LinkAvailableBalanceMonitor.sol
```diff
@@ -266,6 +266,7 @@ contract LinkAvailableBalanceMonitor is AccessControl, AutomationCompatibleInter
     for (uint256 idx = 0; idx < targetAddresses.length; idx++) {
       address targetAddress = targetAddresses[idx];
       contractToFund = s_targets[targetAddress];
+      s_targets[targetAddress].lastTopUpTimestamp = uint56(block.timestamp);
       if (
         localBalance >= contractToFund.topUpAmount &&
         _needsFunding(
@@ -278,12 +279,12 @@ contract LinkAvailableBalanceMonitor is AccessControl, AutomationCompatibleInter
         bool success = i_linkToken.transfer(targetAddress, contractToFund.topUpAmount);
         if (success) {
           localBalance -= contractToFund.topUpAmount;
-          s_targets[targetAddress].lastTopUpTimestamp = uint56(block.timestamp);
           emit TopUpSucceeded(targetAddress);
         } else {
           emit TopUpFailed(targetAddress);
         }
       } else {
+        s_targets[targetAddress].lastTopUpTimestamp = contractToFund.lastTopUpTimestamp;
         emit TopUpBlocked(targetAddress);
       }
     }
```
