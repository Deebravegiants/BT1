# [?] Merge pull request #1495 from lidofinance/fix/pdg-reentrancy

## Summary
Severity: Unknown
Chain: Lido
Component: lidofinance/core
Published: 2025-10-07
Source: https://github.com/lidofinance/core/commit/ed1d5d847db2e2ce209574ab8198e2370b0979cb
Type: security-commit

## Details
Merge pull request #1495 from lidofinance/fix/pdg-reentrancy

fix(PDG): fix reentrancy path in PDG

## Patch
### contracts/0.8.25/vaults/predeposit_guarantee/PredepositGuarantee.sol
```diff
@@ -441,8 +441,8 @@ contract PredepositGuarantee is IPredepositGuarantee, CLProofVerifier, PausableU
 
         // activate validator if possible
         if (stakingVault.depositor() == address(this) && stakingVault.stagedBalance() >= ACTIVATION_DEPOSIT_AMOUNT) {
-            _activateAndTopUpValidator(stakingVault, _witness.pubkey, 0, new bytes(96), withdrawalCredentials, nodeOperator);
             validator.stage = ValidatorStage.ACTIVATED;
+            _activateAndTopUpValidator(stakingVault, _witness.pubkey, 0, new bytes(96), withdrawalCredentials, nodeOperator);
         } else {
             // only if validator is disconnected
             // because on connection we check depositor and staged balance
@@ -655,6 +655,7 @@ contract PredepositGuarantee is IPredepositGuarantee, CLProofVerifier, PausableU
             }
 
             if (stage == ValidatorStage.PROVEN) {
+                validator.stage = ValidatorStage.ACTIVATED;
                 _activateAndTopUpValidator(
                     vault,
                     _pubkey,
@@ -663,7 +664,6 @@ contract PredepositGuarantee is IPredepositGuarantee, CLProofVerifier, PausableU
                     withdrawalCredentials,
                     nodeOperator
                 );
-                validator.stage = ValidatorStage.ACTIVATED;
             } else if (stage == ValidatorStage.ACTIVATED) {
                 _topUpValidator(
                     vault,
```
