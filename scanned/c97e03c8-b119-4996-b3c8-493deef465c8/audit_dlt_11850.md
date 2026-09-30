# [?] fix: crash recovery wait

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2024-11-12
Source: https://github.com/ponder-sh/ponder/commit/eb47559b8589417a9e8a5751db29681cf8fa77f9
Type: security-commit

## Details
fix: crash recovery wait

## Patch
### packages/core/src/database/index.ts
```diff
@@ -828,7 +828,8 @@ export const createDatabase = (args: {
             if (
               isFirstAttempt &&
               args.common.options.command !== "dev" &&
-              crashRecoveryApp?.is_locked === 1
+              (crashRecoveryApp === undefined ||
+                crashRecoveryApp.is_locked === 1)
             ) {
               return {
                 status: "locked",
```
