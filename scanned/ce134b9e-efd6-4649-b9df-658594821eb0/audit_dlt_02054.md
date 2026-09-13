# [?] fix: Prevent UI state corruption race condition (#39407)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-01-25
Source: https://github.com/MetaMask/metamask-extension/commit/cd9f09cb53f426385075d04267d78f0682f0f007
Type: security-commit

## Details
fix: Prevent UI state corruption race condition (#39407)

## **Description**

State changes that occur _after_ a UI connection is initialized, but
_before_ the initial state for that connection is retrieved, could get
erroneously sent to the UI as patches (despite the operations being
represented in the initial state already). Certain types of operations
could corrupt the `metamask` state in the UI if they were repeated this
way (e.g. "delete first entry of array" would delete extra entries if
repeated).

This has been prevented by delaying patch tracking until the exact
moment the initial state for the UI connection is retrieved.

This was easiest to accomplish by adding the initial state as a
parameter to the `startUISync` message, which also has the side- effect
of speeding up initial pageload (one less round-trip between the
background and the UI is needed).

This replaces the `getState` call, which is what the UI used to call to
get the initial background state. This call was surrounded by a
16-second timeout, so that the user would not be stuck waiting forever
if it failed. This timeout logic has been migrated to the
`CriticalStartupErrorHandler` class, and is now based on the
`startUISync` method.

[![Open in GitHub
Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MetaMask/metamask-extension/pull/39407?quickstart=1)

## **Changelog**

CHANGELOG entry: Optimize initial page load and prevent rare temporary
UI state corruption

## **Related issues**

N/A

## **Manual testing steps**

I am not sure how to replicate the state corruption. The example I have
thought of so far is _removing_ an element from an array (as long as
it's not the last element). In that scenario, the patch would be
something like `{ "op": "remove", "path": "/biscuits/0" }`, but the
"removed index" would quickly be replaced by the next item in the array,
hence it's not safe to repeat.

We'd need to find an operation that removed the first element (or
something that _isn't_ the last element) from an array, then try and
trigger that operation at a very specific time during UI initialization
(after the connection is established but before the UI sync completes).

## **Screenshots/Recordings**

N/A

## **Pre-merge author checklist**

- [x] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding
Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [x] I've completed the PR template to the best of my ability
- [x] I’ve included tests if applicable
- [x] I’ve documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [x] I’ve applied the right labels on the PR (see [labeling
guidelines](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/LABELING_GUIDELINES.md)).
Not required for external contributors.

## **Pre-merge reviewer checklist**

- [ ] I've manually tested the PR (e.g. pull and build branch, run the
app, test code being changed).
- [ ] I confirm that this PR addresses all acceptance criteria described
in the ticket it closes and includes the necessary testing evidence such
as recordings and or screenshots.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Prevents duplicate/early patches from corrupting UI state and reduces
startup round-trips by inlining initial state in the UI sync.
> 
> - Introduces `START_UI_SYNC` and moves `BACKGROUND_LIVENESS_METHOD` to
`shared/constants/ui-initialization`; background now sends
`START_UI_SYNC` with the initial state
> - UI listens for `START_UI_SYNC`, passes `initialState` into app boot,
and calls `startSendingPatches` (renamed from `startPatches`)
> - `PatchStore` no longer listens on construct; new `init()` explicitly
starts patch capture; tests updated accordingly
> - Background begins `PatchStore.init()` immediately after computing
initial state for a connection to avoid missed/extra patches
> - Removes `getState` request/timeout flow from UI and
`metaRPCClientFactory`; simplifies request tracking (no per-request
timers); related tests and trace/benchmark metrics removed
> - `CriticalStartupErrorHandler` now tracks liveness and adds a
`START_UI_SYNC`-based initialization timeout for startup failures
> - Minor refactors/renames and import updates across
controller/UI/tests
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
f039b120093103cb9914a3aa06727bf0c8374677. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

---------

Co-authored-by: Jongsun Suh <jongsun.suh@icloud.com>

### app/scripts/background.js
```diff
@@ -28,7 +28,7 @@ import {
   MESSAGE_TYPE,
 } from '../../shared/constants/app';
 import { EXTENSION_MESSAGES } from '../../shared/constants/messages';
-import { BACKGROUND_LIVENESS_METHOD } from '../../shared/constants/background-liveness-check';
+import { BACKGROUND_LIVENESS_METHOD } from '../../shared/constants/ui-initialization';
 import {
   REJECT_NOTIFICATION_CLOSE,
   REJECT_NOTIFICATION_CLOSE_SIG,
```

### app/scripts/lib/PatchStore.test.ts
```diff
@@ -18,7 +18,7 @@ function triggerStateChange(
   newState: Record<string, unknown>,
   patches?: Patch[],
 ) {
-  composableStoreMock.on.mock.calls[0][1]({
+  composableStoreMock.on.mock.calls[0]?.[1]({
     controllerKey: 'test-controller',
     newState,
     oldState,
@@ -36,10 +36,41 @@ describe('PatchStore', () => {
     sanitizePatchesMock.mockImplementation((patches) => patches);
   });
 
+  describe('init', () => {
+    it('begins storing patches', () => {
+      const composableStoreMock = createComposableStoreMock();
+      const patchStore = new PatchStore(composableStoreMock);
+      // Trigger state change before init to ensure it's not tracked
+      triggerStateChange(
+        composableStoreMock,
+        { test1: 'value1' },
+        { test1: 'value2' },
+      );
+
+      patchStore.init();
+      triggerStateChange(
+        composableStoreMock,
+        { test2: 'value1' },
+        { test2: 'value2' },
+      );
+
+      const patches = patchStore.flushPendingPatches();
+      // We only see a patch for the state change _after_ init
+      expect(patches).toEqual([
+        {
+          op: 'replace',
+          path: ['test2'],
+          value: 'value2',
+        },
+      ]);
+    });
+  });
+
   describe('flushPendingPatches', () => {
     it('returns top level patches for composable store events', () => {
       const composableStoreMock = createComposableStoreMock();
       const patchStore = new PatchStore(composableStoreMock);
+      patchStore.init();
 
       triggerStateChange(
         composableStoreMock,
@@ -73,6 +104,7 @@ describe('PatchStore', () => {
       const objectMock = {};
       const composableStoreMock = createComposableStoreMock();
       const patchStore = new PatchStore(composableStoreMock);
+      patchStore.init();
 
       triggerStateChange(
         composableStoreMock,
@@ -106,6 +138,7 @@ describe('PatchStore', () => {
     it('returns empty array if no composable store events', () => {
       const composableStoreMock = createComposableStoreMock();
       const patchStore = new PatchStore(composableStoreMock);
+      patchStore.init();
 
       const patches = patchStore.flushPendingPatches();
 
@@ -115,6 +148,7 @@ describe('PatchStore', () => {
     it('clears pending patches', () => {
       const composableStoreMock = createComposableStoreMock();
       const patchStore = new PatchStore(composableStoreMock);
+      patchStore.init();
 
       triggerStateChange(
         composableStoreMock,
@@ -132,6 +166,7 @@ describe('PatchStore', () => {
     it('sanitizes state in patches', () => {
       const composableStoreMock = createComposableStoreMock();
       const patchStore = new PatchStore(composableStoreMock);
+      patchStore.init();
 
       sanitizeUIStateMock.mockReturnValueOnce({ test2: 'value' });
 
@@ -155,6 +190,7 @@ describe('PatchStore', () => {
     it('adds isInitialized patch if vault in new state', () => {
       const composableStoreMock = createComposableStoreMock();
       const patchStore = new PatchStore(composableStoreMock);
+      patchStore.init();
 
       triggerStateChange(composableStoreMock, { vault: 0 }, { vault: 123 });
 
@@ -177,6 +213,7 @@ describe('PatchStore', () => {
     it('returns patches from composable store events if provided', () => {
       const composableStoreMock = createComposableStoreMock();
       const patchStore = new PatchStore(composableStoreMock);
+      patchStore.init();
 
       triggerStateChange(
         composableStoreMock,
@@ -234,6 +271,7 @@ describe('PatchStore', () => {
 
       const composableStoreMock = createComposableStoreMock();
       const patchStore = new PatchStore(composableStoreMock);
+      patchStore.init();
 
       triggerStateChange(
         composableStoreMock,
@@ -267,6 +305,7 @@ describe('PatchStore', () => {
     it('generates multiple patches if patch has no path', () => {
       const composableStoreMock = createComposableStoreMock();
       const patchStore = new PatchStore(composableStoreMock);
+      patchStore.init();
 
       triggerStateChange(
         composableStoreMock,
@@ -315,6 +354,7 @@ describe('PatchStore', () => {
     it('removes listener from composable store', () => {
       const composableStoreMock = createComposableStoreMock();
       const patchStore = new PatchStore(composableStoreMock);
+      patchStore.init();
 
       patchStore.destroy();
 
```

### app/scripts/lib/PatchStore.ts
```diff
@@ -25,11 +25,16 @@ export class PatchStore {
     this.observableStore = observableStore;
     this.listener = this._onStateChange.bind(this);
 
-    this.observableStore.on('stateChange', this.listener);
-
     log('Created', this.id);
   }
 
+  /**
+   * Start listening for state changes and generating patches.
+   */
+  init() {
+    this.observableStore.on('stateChange', this.listener);
+  }
+
   flushPendingPatches(): Patch[] {
     const patches = this.pendingPatches;
 
```

### app/scripts/lib/metaRPCClientFactory.test.js
```diff
@@ -167,25 +167,6 @@ describe('metaRPCClientFactory', () => {
     });
   });
 
-  it('should be able to handle no message within TIMEOUT secs for getState', async () => {
-    jest.useFakeTimers();
-    const streamTest = createThoughStream();
-    const metaRPCClient = metaRPCClientFactory(streamTest);
-
-    const errorPromise = new Promise((_resolve, reject) =>
-      metaRPCClient.getState('bad').catch((error) => {
-        reject(error);
-      }),
-    );
-
-    jest.runOnlyPendingTimers();
-    await expect(errorPromise).rejects.toThrow(
-      `Background 'getState' call exceeded timeout`,
-    );
-
-    jest.useRealTimers();
-  });
-
   it('should fail all pending actions with a DisconnectError when the stream ends', (done) => {
     const streamTest = createThoughStream();
     const metaRPCClient = metaRPCClientFactory(streamTest);
@@ -199,50 +180,6 @@ describe('metaRPCClientFactory', () => {
     streamTest.emit('end');
   });
 
-  it('should cancel the request timer when handling its response', async () => {
-    jest.useFakeTimers();
-    const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout');
-    const streamTest = createThoughStream();
-    const metaRPCClient = metaRPCClientFactory(streamTest);
-
-    // getState is special, as it is the only method that starts a timeout
-    const requestProm = metaRPCClient.getState();
-
-    const requests = [...metaRPCClient.requests];
-    metaRPCClient.requests.forEach((_, key) => {
-      streamTest.write({
-        jsonrpc: '2.0',
-        id: key,
-        result: 'foobarbaz',
-      });
-    });
-
-    await expect(requestProm).resolves.toStrictEqual('foobarbaz');
-
-    const [, { timer }] = requests[0];
-    expect(clearTimeoutSpy).toHaveBeenCalledWith(timer);
-    jest.useRealTimers();
-  });
-
-  it('should clear pending timers with a DisconnectError when the stream ends', async () => {
-    jest.useFakeTimers();
-    const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout');
-    const streamTest = createThoughStream();
-    const metaRPCClient = metaRPCClientFactory(streamTest);
-
-    // getState is special, as it is the only method that starts a timeout
-    const requestProm = metaRPCClient.getState();
-    const [, { timer }] = [...metaRPCClient.requests][0];
-    streamTest.emit('end');
-
-    await expect(requestProm).rejects.toThrow(
-      new DisconnectError('disconnected'),
-    );
-
-    expect(clearTimeoutSpy).toHaveBeenCalledWith(timer);
-    jest.useRealTimers();
-  });
-
   it('should not throw when receiving junk data over the stream', async () => {
     const streamTest = createThoughStream();
     const metaRPCClient = metaRPCClientFactory(streamTest);
```

### app/scripts/lib/metaRPCClientFactory.ts
```diff
@@ -16,10 +16,6 @@ import type MetamaskController from '../metamask-controller';
 
 const JSON_RPC_VERSION = '2.0' as const;
 
-const SIXTEEN_SECONDS_AS_MILLISECONDS = 16000;
-
-type Timer = ReturnType<typeof setTimeout>;
-
 /**
  * A JSON-RPC 2.0 request object, types with our request types.
  */
@@ -123,7 +119,6 @@ export class MetaRPCClient<Api extends FunctionRegistry<Api>> {
     {
       resolve: (value: Awaited<ReturnType<Api[keyof Api]>>) => void;
       reject: (error: Error) => void;
-      timer?: Timer;
     }
   >();
 
@@ -182,14 +177,7 @@ export class MetaRPCClient<Api extends FunctionRegistry<Api>> {
   async send(payload: JsonRpcApiRequest<Api>) {
     return new Promise<Awaited<ReturnType<Api[typeof payload.method]>>>(
       (resolve, reject) => {
-        let timer: Timer | undefined;
-        if (payload.method === 'getState') {
-          timer = setTimeout(() => {
-            this.requests.delete(payload.id);
-            reject(new Error(`Background 'getState' call exceeded timeout`));
-          }, SIXTEEN_SECONDS_AS_MILLISECONDS);
-        }
-        this.requests.set(payload.id, { resolve, reject, timer });
+        this.requests.set(payload.id, { resolve, reject });
         this.#connectionStream.write(payload);
       },
     );
@@ -226,8 +214,7 @@ export class MetaRPCClient<Api extends FunctionRegistry<Api>> {
     this.#connectionStream.off('end', this.close);
 
     // fail all unfinished requests
-    this.requests.forEach(({ reject, timer }) => {
-      clearTimeout(timer);
+    this.requests.forEach(({ reject }) => {
       reject(new DisconnectError(reason));
     });
     this.requests.clear();
@@ -277,14 +264,12 @@ export class MetaRPCClient<Api extends FunctionRegistry<Api>> {
       e.stack = stack;
       if (request) {
         requests.delete(id);
-        clearTimeout(request.timer);
         request.reject(e);
       } else {
         this.#uncaughtErrorChannel.emit('error', e);
       }
     } else if (request) {
       requests.delete(id);
-      clearTimeout(request.timer);
       request.resolve(response.result);
     }
   };
```

### app/scripts/metamask-controller.js
```diff
@@ -183,6 +183,7 @@ import {
 import { isEqualCaseInsensitive } from '../../shared/modules/string-utils';
 import { parseStandardTokenTransactionData } from '../../shared/modules/transaction.utils';
 import { STATIC_MAINNET_TOKEN_LIST } from '../../shared/constants/tokens';
+import { START_UI_SYNC } from '../../shared/constants/ui-initialization';
 import { getTokenValueParam } from '../../shared/lib/metamask-controller-utils';
 import { isManifestV3 } from '../../shared/modules/mv3.utils';
 import { convertNetworkId } from '../../shared/modules/network.utils';
@@ -2457,7 +2458,6 @@ export default class MetamaskController extends EventEmitter {
 
     return {
       // etc
-      getState: this.getState.bind(this),
       setCurrentCurrency: currencyRateController.setCurrentCurrency.bind(
         currencyRateController,
       ),
@@ -6830,7 +6830,7 @@ export default class MetamaskController extends EventEmitter {
     const api = {
       ...this.getApi(),
       ...this.controllerApi,
-      startPatches: () => {
+      startSendingPatches: () => {
         uiReady = true;
         handleUpdate();
       },
@@ -6850,10 +6850,16 @@ export default class MetamaskController extends EventEmitter {
       if (!isStreamWritable(outStream)) {
         return;
       }
+      // Start tracking patches immediately after retrieving initial state for this UI connection
+      // to ensure we don't miss any patches, or include extra patches.
+      const initialState = this.getState();
+      patchStore.init();
+
       // send notification to client-side
       outStream.write({
         jsonrpc: '2.0',
-        method: 'startUISync',
+        method: START_UI_SYNC,
+        params: [initialState],
       });
     };
 
```

### app/scripts/metamask-controller.test.js
```diff
@@ -1691,14 +1691,6 @@ describe('MetaMaskController', () => {
       });
     });
 
-    describe('#getApi', () => {
-      it('getState', () => {
-        const getApi = metamaskController.getApi();
-        const state = getApi.getState();
-        expect(state).toStrictEqual(metamaskController.getState());
-      });
-    });
-
     describe('hardware keyrings', () => {
       beforeEach(async () => {
         await metamaskController.createNewVaultAndKeychain('test@123');
```

### app/scripts/ui.js
```diff
@@ -115,8 +115,9 @@ async function start() {
   const backgroundConnection = metaRPCClientFactory(subStreams.controller);
   connectToBackground(backgroundConnection, handleStartUISync);
 
-  async function handleStartUISync() {
+  async function handleStartUISync(initialState) {
     endTrace({ name: TraceName.BackgroundConnect });
+    criticalErrorHandler.startUiSyncReceived();
 
     // this means we've received a message from the background, and so
     // background startup has succeed, so we don't need to listen for error
@@ -135,6 +136,7 @@ async function start() {
       backgroundConnection,
       windowType,
       traceContext,
+      initialState,
     );
 
     if (isManifestV3) {
@@ -237,9 +239,15 @@ async function initializeUiWithTab(
   connectionStream,
   windowType,
   traceContext,
+  initialState,
 ) {
   try {
-    const store = await initializeUi(tab, connectionStream, traceContext);
+    const store = await initializeUi(
+      tab,
+      connectionStream,
+      traceContext,
+      initialState,
+    );
 
     endTrace({ name: TraceName.UIStartup });
 
@@ -307,12 +315,18 @@ async function queryCurrentActiveTab(windowType) {
   return { id, title, origin, protocol, url };
 }
 
-async function initializeUi(activeTab, backgroundConnection, traceContext) {
+async function initializeUi(
+  activeTab,
+  backgroundConnection,
+  traceContext,
+  initialState,
+) {
   return await launchMetaMaskUi({
     activeTab,
     container,
     backgroundConnection,
     traceContext,
+    initialState,
   });
 }
 
```

### shared/constants/ui-initialization.ts
```diff
@@ -3,3 +3,9 @@
  * automatically upon connection to prove that the connection is active.
  */
 export const BACKGROUND_LIVENESS_METHOD = 'ALIVE';
+
+/**
+ * This method tells the UI that the background is ready to receive messages, and it includes the
+ * initial background state for the UI process.
+ */
+export const START_UI_SYNC = 'START_UI_SYNC';
```

### shared/lib/trace.ts
```diff
@@ -22,7 +22,6 @@ export enum TraceName {
   DeveloperTest = 'Developer Test',
   DisconnectAllModal = 'Disconnect All Modal',
   FirstRender = 'First Render',
-  GetState = 'Get State',
   ImportNfts = 'Import Nfts',
   ImportTokens = 'Import Tokens',
   InitialActions = 'Initial Actions',
```

### test/e2e/benchmarks/constants.ts
```diff
@@ -9,7 +9,6 @@ export const ALL_METRICS = {
   firstPaint: 'paint["first-paint"]',
   backgroundConnect: 'Background Connect',
   firstReactRender: 'First Render',
-  getState: 'Get State',
   initialActions: 'Initial Actions',
   loadScripts: 'Load Scripts',
   setupStore: 'Setup Store',
```

### test/e2e/benchmarks/types-generated.ts
```diff
@@ -11,7 +11,6 @@ export type Metrics = {
   'UI Startup': number;
   'Background Connect': number;
   'First Render': number;
-  'Get State': number;
   'Initial Actions': number;
   'Load Scripts': number;
   'Setup Store': number;
```
