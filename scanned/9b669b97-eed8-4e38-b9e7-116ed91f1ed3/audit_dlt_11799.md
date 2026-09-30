# [?] fix: incoming transaction polling race condition (#6913)

## Summary
Severity: Unknown
Chain: Tooling
Component: MetaMask/core
Published: 2025-10-22
Source: https://github.com/MetaMask/core/commit/f636954d1c4222b916f9bf50dbb60e9b50f9e2db
Type: security-commit

## Details
fix: incoming transaction polling race condition (#6913)

## Explanation

Prevent multiple simultaneous timeouts being created if `stop` and
`start` are called while a previous asynchronous update is still in
progress.

## References

## Checklist

- [x] I've updated the test suite for new or updated code as appropriate
- [x] I've updated documentation (JSDoc, Markdown, etc.) for new or
updated code as appropriate
- [x] I've communicated my changes to consumers by [updating changelogs
for packages I've
changed](https://github.com/MetaMask/core/tree/main/docs/contributing.md#updating-changelogs),
highlighting breaking changes as necessary
- [x] I've prepared draft pull requests for clients and consumer
packages to resolve any breaking changes

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Prevent duplicate timers and concurrent updates in
`IncomingTransactionHelper` by tracking in-progress updates and clearing
timeouts, with tests and changelog updated.
> 
> - **Transaction polling (Incoming)**:
> - Update `IncomingTransactionHelper` to track in-progress updates with
`#isUpdating`, preventing additional intervals from being queued while
an update is running.
> - Clear any existing timeout before scheduling the next interval to
avoid duplicate timers.
> - **Tests**:
> - Add test ensuring repeated `start`/`stop` calls during an ongoing
update only schedule one timeout and perform a single
`fetchTransactions` call.
> - **Changelog**:
> - Add Unreleased fix entry: prevent race condition causing excessive
incoming transaction polling.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
4cf12fec87b79f29f6082131ad92c8c35272a58a. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### packages/transaction-controller/CHANGELOG.md
```diff
@@ -7,6 +7,10 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ## [Unreleased]
 
+### Fixed
+
+- Prevent race condition causing excessive incoming transaction polling ([#6913](https://github.com/MetaMask/core/pull/6913))
+
 ## [60.9.0]
 
 ### Added
```

### packages/transaction-controller/src/helpers/IncomingTransactionHelper.test.ts
```diff
@@ -376,6 +376,31 @@ describe('IncomingTransactionHelper', () => {
 
       expect(jest.getTimerCount()).toBe(0);
     });
+
+    it('does not queue additional updates if first is still running', async () => {
+      const remoteTransactionSource = createRemoteTransactionSourceMock([]);
+
+      const helper = new IncomingTransactionHelper({
+        ...CONTROLLER_ARGS_MOCK,
+        remoteTransactionSource,
+      });
+
+      helper.start();
+      helper.stop();
+
+      helper.start();
+      helper.stop();
+
+      helper.start();
+
+      await flushPromises();
+
+      expect(jest.getTimerCount()).toBe(1);
+
+      expect(remoteTransactionSource.fetchTransactions).toHaveBeenCalledTimes(
+        1,
+      );
+    });
   });
 
   describe('stop', () => {
```

### packages/transaction-controller/src/helpers/IncomingTransactionHelper.ts
```diff
@@ -45,6 +45,8 @@ export class IncomingTransactionHelper {
 
   #isRunning: boolean;
 
+  #isUpdating: boolean;
+
   readonly #messenger: TransactionControllerMessenger;
 
   readonly #remoteTransactionSource: RemoteTransactionSource;
@@ -88,6 +90,7 @@ export class IncomingTransactionHelper {
     this.#includeTokenTransfers = includeTokenTransfers;
     this.#isEnabled = isEnabled ?? (() => true);
     this.#isRunning = false;
+    this.#isUpdating = false;
     this.#messenger = messenger;
     this.#remoteTransactionSource = remoteTransactionSource;
     this.#trimTransactions = trimTransactions;
@@ -109,6 +112,10 @@ export class IncomingTransactionHelper {
 
     this.#isRunning = true;
 
+    if (this.#isUpdating) {
+      return;
+    }
+
     this.#onInterval().catch((error) => {
       log('Initial polling failed', error);
     });
@@ -129,13 +136,21 @@ export class IncomingTransactionHelper {
   }
 
   async #onInterval() {
+    this.#isUpdating = true;
+
     try {
       await this.update({ isInterval: true });
     } catch (error) {
       console.error('Error while checking incoming transactions', error);
     }
 
+    this.#isUpdating = false;
+
     if (this.#isRunning) {
+      if (this.#timeoutId) {
+        clearTimeout(this.#timeoutId as number);
+      }
+
       this.#timeoutId = setTimeout(
         // eslint-disable-next-line @typescript-eslint/no-misused-promises
         () => this.#onInterval(),
```
