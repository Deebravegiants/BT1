# [?] fix overflow

## Summary
Severity: Unknown
Chain: Astar
Component: AstarNetwork/Astar
Published: 2020-05-12
Source: https://github.com/AstarNetwork/Astar/commit/f4e42fc507a4c5efadc9866baf284b24682910a6
Type: security-commit

## Details
fix overflow

## Patch
### frame/dapps-staking/src/lib.rs
```diff
@@ -896,17 +896,19 @@ impl<T: Trait> Module<T> {
     ) {
         let era = nominations.submitted_in + 1;
         for (target, value) in nominations.targets.iter() {
-            <ErasStakingPoints<T>>::mutate(&era, &target, |points| {
-                (*points).total -= value.clone();
-                (*points).individual.remove(stash);
-            });
+            if let Some(operator) = T::ContractFinder::operator(&target) {
+                <ErasStakingPoints<T>>::mutate(&era, &operator, |points| {
+                    (*points).total = points.total.saturating_sub(value.clone());
+                    (*points).individual.remove(stash);
+                });
+            }
 
             <ErasNominateTotals<T>>::mutate(&era, stash, |total| {
-                *total -= value.clone();
+                *total = total.saturating_sub(value.clone());
             });
 
             <ErasTotalStake<T>>::mutate(&era, |total| {
-                *total -= value.clone();
+                *total = total.saturating_sub(value.clone());
             });
         }
         <DappsNominations<T>>::remove(stash);
```
