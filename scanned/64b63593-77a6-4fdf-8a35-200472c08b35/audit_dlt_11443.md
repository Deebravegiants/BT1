# [?] Reentrancy guard corner case (#12508)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2024-03-22
Source: https://github.com/smartcontractkit/ccip/commit/88e5e575c42a20edb92c14e05a10ffd33b33a0f6
Type: security-commit

## Details
Reentrancy guard corner case (#12508)

* add reentrancy guard

Signed-off-by: Borja Aranda <borja.aranda@smartcontract.com>

* reentrancy guard: add corner case

Signed-off-by: Borja Aranda <borja.aranda@smartcontract.com>

---------

Signed-off-by: Borja Aranda <borja.aranda@smartcontract.com>

## Patch
### contracts/src/v0.8/automation/upkeeps/LinkAvailableBalanceMonitor.sol
```diff
@@ -281,6 +281,7 @@ contract LinkAvailableBalanceMonitor is AccessControl, AutomationCompatibleInter
           localBalance -= contractToFund.topUpAmount;
           emit TopUpSucceeded(targetAddress);
         } else {
+          s_targets[targetAddress].lastTopUpTimestamp = contractToFund.lastTopUpTimestamp;
           emit TopUpFailed(targetAddress);
         }
       } else {
```
