# [?] Fix race condition which could cause duties to not be invalidated (#3857)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2021-04-14
Source: https://github.com/Consensys-Incorporated/teku/commit/b782b1d64b6540516455b1d4815e25dab8044078
Type: security-commit

## Details
Fix race condition which could cause duties to not be invalidated (#3857)

## Patch
### CHANGELOG.md
```diff
@@ -15,4 +15,5 @@ For information on changes in released versions of Teku, see the [releases page]
 - Early access: Support for automatic fail-over of eth1-endpoints.  Multiple endpoints can be specified with the new `--eth1-endpoints` CLI option. Thanks to Enrico Del Fante. 
 
 ### Bug Fixes
-- Fixed issue where attestation subnets were not unsubscribed from leading to unnecessary CPU load when running small numbers of validators.
\ No newline at end of file
+- Fixed issue where attestation subnets were not unsubscribed from leading to unnecessary CPU load when running small numbers of validators.
+- Fixed issue where validator duties were not invalidated in response to new blocks correctly when using dependent roots.
\ No newline at end of file
```

### validator/client/src/main/java/tech/pegasys/teku/validator/client/EpochDuties.java
```diff
@@ -82,7 +82,7 @@ public synchronized void cancel() {
     pendingActions.clear();
   }
 
-  private void processPendingActions(final Optional<ScheduledDuties> scheduledDuties) {
+  private synchronized void processPendingActions(final Optional<ScheduledDuties> scheduledDuties) {
     if (pendingHeadUpdate.isPresent()
         && scheduledDuties.isPresent()
         && requiresRecalculation(scheduledDuties.get(), pendingHeadUpdate.get())) {
```
