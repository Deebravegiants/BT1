# [?] fix(core-backend): race condition in connection (#6842)

## Summary
Severity: Unknown
Chain: Tooling
Component: MetaMask/core
Published: 2025-10-15
Source: https://github.com/MetaMask/core/commit/cc573933e26c21946352e9933eff2d30ee150c72
Type: security-commit

## Details
fix(core-backend): race condition in connection (#6842)

## Explanation

### What is the current state and why does it need to change?

This PR addresses two improvements to the core backend services:

**1. Race Condition Fix in `BackendWebSocketService`**

The `BackendWebSocketService.connect()` method had a race condition that
could create multiple concurrent WebSocket connections when called
simultaneously from multiple event sources. This could happen when:
- `KeyringController:unlock` triggers a connection
- `AuthenticationController:stateChange` triggers a connection  
- `MetaMaskController.isClientOpen` triggers a connection

All these events could fire at nearly the same time, and each would
check if a connection existed, find none (because the promise wasn't set
yet), and start creating a new WebSocket connection.

**2. Performance Tracing in `AccountActivityService`**

There was no visibility into transaction delivery latency - the time
between when a transaction occurs on-chain and when we receive
notification about it. This metric is critical for monitoring backend
performance and user experience.

### What is the solution and how does it work?

**Race Condition Fix:**
The fix ensures the connection promise is set **synchronously** before
any async operations begin. This prevents duplicate connections by:
1. Immediately setting `this.#connectionPromise` at the start of
`connect()`
2. Only then proceeding with async authentication and WebSocket creation
3. Any subsequent `connect()` calls will see the existing promise and
return it instead of creating a new connection

**Performance Tracing:**
Added optional `traceFn` parameter to `AccountActivityService`
constructor that:
1. Accepts a trace callback (e.g., Sentry performance monitoring)
2. Traces transaction message receipt in `#handleAccountActivityUpdate`
3. Captures `chain`, `status`, and `elapsed_ms` (time from transaction
timestamp to message arrival)
4. Defaults to no-op to keep the service platform-agnostic

### Changes whose purpose might not be obvious?

**Race Condition Fix:** The promise assignment happens before the `try`
block to ensure it's set even if authentication or connection fails.
This prevents a scenario where a failed connection attempt leaves the
service in an inconsistent state where it thinks it's connecting but has
no promise to track.

**Performance Tracing:** The trace wraps the actual message processing
callback, ensuring accurate measurement of both the delivery latency and
the processing time. The `elapsed_ms` metric measures from the
transaction's on-chain timestamp (in the transaction data) to when we
receive the WebSocket message, giving us true end-to-end latency.

## References

## Checklist

- [x] I've updated the test suite for new or updated code as appropriate
- [x] I've updated documentation (JSDoc, Markdown, etc.) for new or
updated code as appropriate
- [x] I've communicated my changes to consumers by updating changelogs
for packages I've changed, highlighting breaking changes as necessary
- [ ] I've prepared draft pull requests for clients and consumer
packages to resolve any breaking changes

**Note:** This PR includes a bug fix (race condition) and a new feature
(performance tracing) with no breaking changes. CHANGELOG has been
updated to document both changes.


<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Fixes a race in WebSocket connect() to ensure a single connection and
adds optional tracing to AccountActivityService for transaction delivery
latency.
> 
> - **Backend**:
> - **WebSocket connection**: Make `connect()` idempotent by
synchronously setting `#connectionPromise` before async auth/connection,
preventing parallel connections; improved error propagation.
> - **Tracing**: Minor adjustments to channel/notification tracing
payloads.
> - **AccountActivityService**:
>   - Add optional `traceFn` to options; default no-op.
> - Trace transaction message receipt with `elapsed_ms`, wrapping
publishes to `transactionUpdated` and `balanceUpdated`.
> - **Tests**:
> - Add concurrency tests ensuring multiple `connect()` calls create
only one WebSocket, including interleaved auth scenarios; update auth
error expectations.
> - **Changelog**:
> - Document added `traceFn` in `AccountActivityService` and race fix in
`BackendWebSocketService.connect()` under Unreleased.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
0e217c44e7a7bf93c06487b5aabe7c246d5a16ad. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### packages/core-backend/CHANGELOG.md
```diff
@@ -7,6 +7,17 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ## [Unreleased]
 
+### Added
+
+- Add optional `traceFn` parameter to `AccountActivityService` constructor for performance tracing integration ([#6842](https://github.com/MetaMask/core/pull/6842))
+  - Enables tracing of transaction message receipt with elapsed time from transaction timestamp to message arrival
+  - Trace captures `chain`, `status`, and `elapsed_ms` for monitoring transaction delivery latency
+
+### Fixed
+
+- Fix race condition in `BackendWebSocketService.connect()` that could create multiple concurrent WebSocket connections when called simultaneously from multiple event sources (e.g., `KeyringController:unlock`, `AuthenticationController:stateChange`, and `MetaMaskController.isClientOpen`) ([#6842](https://github.com/MetaMask/core/pull/6842))
+  - Connection promise is now set synchronously before any async operations to prevent duplicate connections
+
 ## [2.0.0]
 
 ### Added
```

### packages/core-backend/src/AccountActivityService.ts
```diff
@@ -10,6 +10,7 @@ import type {
   AccountsControllerSelectedAccountChangeEvent,
 } from '@metamask/accounts-controller';
 import type { RestrictedMessenger } from '@metamask/base-controller';
+import type { TraceCallback } from '@metamask/controller-utils';
 import type { InternalAccount } from '@metamask/keyring-internal-api';
 
 import type { AccountActivityServiceMethodActions } from './AccountActivityService-method-action-types';
@@ -64,6 +65,8 @@ export type SubscriptionOptions = {
 export type AccountActivityServiceOptions = {
   /** Custom subscription namespace (default: 'account-activity.v1') */
   subscriptionNamespace?: string;
+  /** Optional callback to trace performance of account activity operations (default: no-op) */
+  traceFn?: TraceCallback;
 };
 
 // =============================================================================
@@ -189,7 +192,9 @@ export class AccountActivityService {
 
   readonly #messenger: AccountActivityServiceMessenger;
 
-  readonly #options: Required<AccountActivityServiceOptions>;
+  readonly #options: Required<Omit<AccountActivityServiceOptions, 'traceFn'>>;
+
+  readonly #trace: TraceCallback;
 
   // Track chains that are currently up (based on system notifications)
   readonly #chainsUp: Set<string> = new Set();
@@ -216,6 +221,12 @@ export class AccountActivityService {
         options.subscriptionNamespace ?? SUBSCRIPTION_NAMESPACE,
     };
 
+    // Default to no-op trace function to keep core platform-agnostic
+    this.#trace =
+      options.traceFn ??
+      // eslint-disable-next-line @typescript-eslint/no-explicit-any
+      (((_request: any, fn?: any) => fn?.()) as TraceCallback);
+
     this.#messenger.registerMethodActionHandlers(
       this,
       MESSENGER_EXPOSED_METHODS,
@@ -335,20 +346,45 @@ export class AccountActivityService {
   #handleAccountActivityUpdate(payload: AccountActivityMessage): void {
     const { address, tx, updates } = payload;
 
+    // Calculate time elapsed between transaction time and message receipt
+    const txTimestampMs = tx.timestamp * 1000; // Convert Unix timestamp (seconds) to milliseconds
+    const elapsedMs = Date.now() - txTimestampMs;
+
     log('Handling account activity update', {
       address,
       updateCount: updates.length,
+      elapsedMs,
     });
 
-    // Process transaction update
-    this.#messenger.publish(`AccountActivityService:transactionUpdated`, tx);
+    // Trace message receipt with latency from transaction time to now
+    this.#trace(
+      {
+        name: `${SERVICE_NAME} Transaction Message`,
+        data: {
+          chain: tx.chain,
+          status: tx.status,
+          elapsed_ms: elapsedMs,
+        },
+        tags: {
+          service: SERVICE_NAME,
+          notification_type: this.#options.subscriptionNamespace,
+        },
+      },
+      () => {
+        // Process transaction update
+        this.#messenger.publish(
+          `AccountActivityService:transactionUpdated`,
+          tx,
+        );
 
-    // Publish comprehensive balance updates with transfer details
-    this.#messenger.publish(`AccountActivityService:balanceUpdated`, {
-      address,
-      chain: tx.chain,
-      updates,
-    });
+        // Publish comprehensive balance updates with transfer details
+        this.#messenger.publish(`AccountActivityService:balanceUpdated`, {
+          address,
+          chain: tx.chain,
+          updates,
+        });
+      },
+    );
   }
 
   /**
```

### packages/core-backend/src/BackendWebSocketService.test.ts
```diff
@@ -38,6 +38,17 @@ class MockWebSocket extends EventTarget {
 
   public static readonly CLOSED = 3;
 
+  // Track total instances created for testing
+  private static instanceCount = 0;
+
+  public static getInstanceCount(): number {
+    return MockWebSocket.instanceCount;
+  }
+
+  public static resetInstanceCount(): void {
+    MockWebSocket.instanceCount = 0;
+  }
+
   // WebSocket properties
   public readyState: number = MockWebSocket.CONNECTING;
 
@@ -74,6 +85,7 @@ class MockWebSocket extends EventTarget {
     { autoConnect = true }: { autoConnect?: boolean } = {},
   ) {
     super();
+    MockWebSocket.instanceCount += 1;
     this.url = url;
     // TypeScript has issues with jest.spyOn on WebSocket methods, so using direct assignment
     // eslint-disable-next-line jest/prefer-spy-on
@@ -361,6 +373,8 @@ async function withService<ReturnValue>(
   const [{ options = {}, mockWebSocketOptions = {} }, testFunction] =
     args.length === 2 ? args : [{}, args[0]];
 
+  MockWebSocket.resetInstanceCount();
+
   const setup = setupBackendWebSocketService({ options, mockWebSocketOptions });
 
   try {
@@ -504,6 +518,97 @@ describe('BackendWebSocketService', () => {
       });
     });
 
+    it('should prevent race condition when multiple concurrent connect() calls are made', async () => {
+      await withService(async ({ service }) => {
+        // Simulate multiple concurrent connect() calls (as would happen from
+        // KeyringController:unlock, AuthenticationController:stateChange, and
+        // MetaMaskController.isClientOpen all firing at once)
+        const connectPromises = [
+          service.connect(),
+          service.connect(),
+          service.connect(),
+        ];
+
+        // Wait for all promises to resolve
+        await Promise.all(connectPromises);
+
+        // Verify only ONE WebSocket connection was created
+        expect(MockWebSocket.getInstanceCount()).toBe(1);
+
+        // Verify service is in CONNECTED state
+        const connectionInfo = service.getConnectionInfo();
+        expect(connectionInfo.state).toBe(WebSocketState.CONNECTED);
+      });
+    });
+
+    it('should handle rapid sequential connect() calls after promise clears without creating duplicates', async () => {
+      await withService(async ({ service }) => {
+        // First connection
+        await service.connect();
+        expect(MockWebSocket.getInstanceCount()).toBe(1);
+        expect(service.getConnectionInfo().state).toBe(
+          WebSocketState.CONNECTED,
+        );
+
+        // Multiple calls after connection is established should not create new connections
+        await Promise.all([
+          service.connect(),
+          service.connect(),
+          service.connect(),
+        ]);
+
+        // Should still be only 1 connection
+        expect(MockWebSocket.getInstanceCount()).toBe(1);
+        expect(service.getConnectionInfo().state).toBe(
+          WebSocketState.CONNECTED,
+        );
+      });
+    });
+
+    it('should handle interleaved connect() calls during async getBearerToken without duplicates', async () => {
+      await withService(
+        { mockWebSocketOptions: { autoConnect: false } },
+        async ({ service, getMockWebSocket, mocks }) => {
+          // Make getBearerToken async to simulate the race window
+          let getBearerTokenResolve: ((value: string) => void) | null = null;
+          mocks.getBearerToken.mockImplementation(() => {
+            return new Promise<string>((resolve) => {
+              getBearerTokenResolve = resolve;
+            });
+          });
+
+          // Start first connect (will wait on getBearerToken)
+          const connect1 = service.connect();
+
+          // Immediately start second connect (should wait for first)
+          const connect2 = service.connect();
+
+          // Immediately start third connect (should also wait)
+          const connect3 = service.connect();
+
+          // Now resolve the getBearerToken
+          expect(getBearerTokenResolve).not.toBeNull();
+          // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
+          getBearerTokenResolve!('test-token');
+
+          // Wait a tick for the token resolution to propagate
+          await flushPromises();
+
+          // Manually trigger WebSocket open
+          getMockWebSocket().triggerOpen();
+
+          // Wait for all connections to complete
+          await Promise.all([connect1, connect2, connect3]);
+
+          // Should only have created ONE WebSocket
+          expect(MockWebSocket.getInstanceCount()).toBe(1);
+          expect(service.getConnectionInfo().state).toBe(
+            WebSocketState.CONNECTED,
+          );
+        },
+      );
+    });
+
     it('should handle connection timeout by rejecting with timeout error and setting state to ERROR', async () => {
       await withService(
         {
@@ -1366,7 +1471,10 @@ describe('BackendWebSocketService', () => {
         },
         async ({ service, mocks }) => {
           mocks.getBearerToken.mockResolvedValueOnce(null);
-          await service.connect();
+
+          await expect(service.connect()).rejects.toThrow(
+            'Authentication required: user not signed in',
+          );
 
           expect(service.getConnectionInfo().state).toBe(
             WebSocketState.DISCONNECTED,
@@ -1383,8 +1491,10 @@ describe('BackendWebSocketService', () => {
           mockWebSocketOptions: { autoConnect: false },
         },
         async ({ service, mocks }) => {
-          mocks.getBearerToken.mockRejectedValueOnce(new Error('Auth error'));
-          await service.connect();
+          const authError = new Error('Auth error');
+          mocks.getBearerToken.mockRejectedValueOnce(authError);
+
+          await expect(service.connect()).rejects.toThrow('Auth error');
 
           expect(service.getConnectionInfo().state).toBe(
             WebSocketState.DISCONNECTED,
```

### packages/core-backend/src/BackendWebSocketService.ts
```diff
@@ -437,44 +437,50 @@ export class BackendWebSocketService {
     }
 
     // If already connecting, wait for the existing connection attempt to complete
-    if (this.#state === WebSocketState.CONNECTING && this.#connectionPromise) {
+    if (this.#connectionPromise) {
       await this.#connectionPromise;
       return;
     }
 
-    // Priority 2: Check authentication requirements (signed in)
-    let bearerToken: string;
-    try {
-      const token = await this.#messenger.call(
-        'AuthenticationController:getBearerToken',
-      );
-      if (!token) {
+    // Create and store the connection promise IMMEDIATELY (before any async operations)
+    // This ensures subsequent connect() calls will wait for this promise instead of creating new connections
+    this.#connectionPromise = (async () => {
+      // Priority 2: Check authentication requirements (signed in)
+      let bearerToken: string;
+      try {
+        const token = await this.#messenger.call(
+          'AuthenticationController:getBearerToken',
+        );
+        if (!token) {
+          this.#scheduleReconnect();
+          throw new Error('Authentication required: user not signed in');
+        }
+        bearerToken = token;
+      } catch (error) {
+        log('Failed to check authentication requirements', { error });
+
+        // Can't connect - schedule retry
         this.#scheduleReconnect();
-        return;
+        throw error;
       }
-      bearerToken = token;
-    } catch (error) {
-      log('Failed to check authentication requirements', { error });
 
-      // Can't connect - schedule retry
-      this.#scheduleReconnect();
-      return;
-    }
+      this.#setState(WebSocketState.CONNECTING);
 
-    this.#setState(WebSocketState.CONNECTING);
+      // Establish the actual WebSocket connection
+      try {
+        await this.#establishConnection(bearerToken);
+      } catch (error) {
+        const errorMessage = getErrorMessage(error);
+        log('Connection attempt failed', { errorMessage, error });
+        this.#setState(WebSocketState.ERROR);
 
-    // Create and store the connection promise
-    this.#connectionPromise = this.#establishConnection(bearerToken);
+        // Rethrow to propagate error to caller
+        throw error;
+      }
+    })();
 
     try {
       await this.#connectionPromise;
-    } catch (error) {
-      const errorMessage = getErrorMessage(error);
-      log('Connection attempt failed', { errorMessage, error });
-      this.#setState(WebSocketState.ERROR);
-
-      // Rethrow to propagate error to caller
-      throw error;
     } finally {
       // Clear the connection promise when done (success or failure)
       this.#connectionPromise = null;
@@ -1154,13 +1160,11 @@ export class BackendWebSocketService {
       {
         name: `${SERVICE_NAME} Channel Message`,
         data: {
-          channel: message.channel,
           latency_ms: latency,
           event: message.event,
         },
         tags: {
           service: SERVICE_NAME,
-          channel_type: message.channel,
         },
       },
       () => {
@@ -1190,7 +1194,7 @@ export class BackendWebSocketService {
       const receivedAt = Date.now();
       const latency = receivedAt - timestamp;
 
-      // Trace notification processing with latency data
+      // Trace notification processing wi th latency data
       // Use stored channelType instead of parsing each time
       this.#trace(
         {
```
