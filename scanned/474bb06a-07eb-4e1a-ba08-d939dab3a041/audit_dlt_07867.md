# [?] Fix defect crash.

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2025-12-01
Source: https://github.com/status-im/nimbus-eth2/commit/b30deb4308f846d9c5fa20ed036423a384437140
Type: security-commit

## Details
Fix defect crash.

## Patch
### beacon_chain/sync/sync_queue.nim
```diff
@@ -283,7 +283,7 @@ func getShortMap*[T](
 ): string =
   let
     alphabet =
-      "123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/#"
+      "123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/#-"
     unknown = "…"
 
   var
```
