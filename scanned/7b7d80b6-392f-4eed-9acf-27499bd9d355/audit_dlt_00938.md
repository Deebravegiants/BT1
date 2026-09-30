# [?] fix: fixed race condition on vault creation and get seedphrase (#44276)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-07-13
Source: https://github.com/MetaMask/metamask-extension/commit/e9d9c6cd75085859e8702f945e43f7f1dd793a9d
Type: security-commit

## Details
fix: fixed race condition on vault creation and get seedphrase (#44276)

## **Description**

### Context

Fixes
[#44068](https://github.com/MetaMask/metamask-extension/issues/44068) —
an intermittent E2E failure in `reset-wallet.spec.ts` during the
**second** onboarding pass after wallet reset. The failure surfaces as:

```
OnboardingFlow: failed to create new account Error: Keyring not found
Error creating password Error: Keyring not found
```

`Keyring not found` is thrown from
`KeyringController.exportSeedPhrase()` when the HD keyring has been
cleared from memory mid-export (`keyrings[0]?.keyring` is falsy). On the
create-wallet path this happens via `createNewVaultAndGetSeedPhrase` →
`getSeedPhrase` → `exportSeedPhrase`.

### Root cause (confirmed)

This was **reproduced locally** with the same error signature as CI.

MetaMask can have **multiple UI surfaces** open at once (main window +
side panel). They share one background, but each has its **own Redux
store**.

On second-pass onboarding password submit, the main window:

1. `createNewVault` — creates the vault and unlocks it
2. `getSeedPhrase` — exports the recovery phrase

Previously these were **two separate background RPCs** with
`createVaultMutex` released between them. Meanwhile, a **stale side
panel** (left open after first onboarding) could react to `isUnlocked:
true` while onboarding was still incomplete. Its routing reaches the
onboarding **lock trap** (`OnboardingFlowSwitch` → `LOCK_ROUTE` →
`setLocked`), which clears in-memory keyrings **during** step 2 →
`Keyring not found`.

**Why it flakes in CI / reset-wallet E2E:** The spec runs reset and
second onboarding back-to-back with no human delay. The side panel can
lag on `/unlock` or `/` while the main window races ahead to password
submit. The dangerous window also exists in production whenever crypto
work widens the gap between create and export, or when any new surface
boots at `/` during export.

**In short:** the main window exports the seed phrase while another
surface locks the wallet.

### Fix

**1. Background — atomic vault + export under one mutex**

- Added `createNewVaultAndGetSeedPhrase(password)` — holds
`createVaultMutex` through vault creation **and** seed export.
- Added `unlockAndGetSeedPhrase(password)` — same mutex through unlock +
export (import rehydration path).
- Refactored vault creation into
`_createNewVaultAndKeychainUnderLock(password)`;
`createNewVaultAndKeychain` delegates to it (behavior unchanged).
- Passed `createVaultMutex` into `LegacyBackgroundApiService` so
**`setLocked` also acquires it** — lock requests wait until vault
create/export completes.

**2. UI — single RPC thunks**

- `createNewVaultAndGetSeedPhrase` → one background call (was
`createNewVault` + `getSeedPhrase`).
- `unlockAndGetSeedPhrase` → one background call (was `submitPassword` +
`getSeedPhrase`).
- `createNewVaultAndSyncWithSocial` → uses
`createNewVaultAndGetSeedPhrase`, then social backup.

**3. UI — side panel mitigation**

- Added `useCloseSidePanelOnWalletReset` (wired in
`routes.component.tsx`).
- When the side panel sees `isWalletResetInProgress` from shared
background state, it calls `window.close()` so a stale panel cannot
enter the onboarding lock trap during second-pass onboarding.

**4. UI — duplicate submit guard**

- `create-password.tsx`: `isSubmitting` state + `loading` on the form to
block double password submit.

**5. Tests**

- `metamask-controller.actions.test.js` —
`createNewVaultAndGetSeedPhrase`, `unlockAndGetSeedPhrase`.
- `ui/store/actions.test.js` — single-RPC thunks, updated social-create
path.
- `ui/hooks/useCloseSidePanelOnWalletReset.test.ts` — side panel close
behavior.
- `create-password.test.tsx` — submit guard.

## **Changelog**

CHANGELOG entry: null

## **Related issues**

Fixes: #44068

## **Manual testing steps**

1. Build a test extension: `yarn build:test`
2. Run the failing E2E spec (repeat to check for flakiness):
   ```bash
yarn test:e2e:single test/e2e/tests/reset-wallet/reset-wallet.spec.ts
--browser=chrome
   ```
3. **Standard create-wallet onboarding**
   - Fresh profile → complete onboarding with new SRP.
   - Confirm password creation succeeds and SRP backup appears.
4. **Reset-wallet flow (main repro scenario)**
- Complete first onboarding (side panel left open from onboarding
completion).
- Lock wallet → Forgot password → "I don't know my Recovery Phrase" →
Reset wallet.
   - Complete second onboarding with a new password.
   - Confirm onboarding completes without `Keyring not found`.
   - Confirm side panel closes when reset starts (if still open).
5. **Import unlock path**
   - Start import onboarding, submit password on unlock step.
   - Confirm no `Keyring not found` during seed retrieval.
6. Confirm create-password submit is disabled while the request is in
flight (double-click does not fire a second submission).

<!--
## **Screenshots/Recordings**
### **Before**
### **After**
-->

## **Pre-merge author checklist**

- [x] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding
Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [x] I've completed the PR template to the best of my ability
- [x] I've included tests if applicable
- [x] I've documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [x] I've applied the right labels on the PR (see [labeling
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
> **High Risk**
> Changes vault creation, unlock, seed export, and locking serialization
across background and UI—security-sensitive keyring paths where races
previously caused data-loss-class failures.
> 
> **Overview**
> Fixes an intermittent **Keyring not found** failure during second-pass
onboarding when vault creation and seed export were separate RPCs and
another UI surface could lock the wallet in between.
> 
> The background now exposes **`createNewVaultAndGetSeedPhrase`** and
**`unlockAndGetSeedPhrase`**, each holding **`createVaultMutex`**
through vault work and seed export.
**`LegacyBackgroundApiService:setLocked`** also acquires that mutex so
locks wait until create/export finishes. UI thunks call the single-RPC
methods instead of create/unlock then **`getSeedPhrase`**, with shared
**`encodeSeedPhraseForBackground`** /
**`decodeSeedPhraseFromBackground`** for seed bytes over the port.
> 
> **`useCloseSidePanelOnWalletReset`** closes the side panel when
**`isWalletResetInProgress`** is set so a stale panel cannot hit the
onboarding lock trap. Create-password adds **`isSubmitting`** / form
**`loading`** to block double submit.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit
a740b426734cfa9bb84b048a16827e4ec544008a. Bugbot is set up for automated
code reviews on this repo. Configure
[here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

### app/scripts/messenger-client-init/legacy-background-api-service-init.test.ts
```diff
@@ -42,6 +42,7 @@ describe('LegacyBackgroundApiServiceInit', () => {
       infuraProjectId: undefined,
       offscreenPromise: expect.any(Promise),
       seedlessOperationMutex: undefined,
+      createVaultMutex: undefined,
       sendUpdate: undefined,
     });
   });
```

### app/scripts/messenger-client-init/legacy-background-api-service-init.ts
```diff
@@ -14,6 +14,7 @@ import { MessengerClientInitFunction } from './types';
  * @param request.getOpenMetamaskTabsIds - A function that returns a record of open MetaMask tab IDs.
  * @param request.sendUpdate - A function to send updates to the UI.
  * @param request.seedlessOperationMutex - A mutex to use for seedless operations.
+ * @param request.createVaultMutex - A mutex to serialize vault creation/export with locking.
  * @param request.offscreenPromise - A promise that resolves when the offscreen document is ready.
  * @returns The initialized service.
  */
@@ -27,6 +28,7 @@ export const LegacyBackgroundApiServiceInit: MessengerClientInitFunction<
   getOpenMetamaskTabsIds,
   sendUpdate,
   seedlessOperationMutex,
+  createVaultMutex,
   offscreenPromise,
 }) => {
   const messengerClient = new LegacyBackgroundApiService({
@@ -36,6 +38,7 @@ export const LegacyBackgroundApiServiceInit: MessengerClientInitFunction<
     getOpenMetamaskTabsIds,
     sendUpdate,
     seedlessOperationMutex,
+    createVaultMutex,
     offscreenPromise,
   });
 
```

### app/scripts/messenger-client-init/types.ts
```diff
@@ -155,6 +155,11 @@ export type MessengerClientInitRequest<
    */
   seedlessOperationMutex: Mutex;
 
+  /**
+   * The mutex used to serialize vault creation, seed export, and locking.
+   */
+  createVaultMutex: Mutex;
+
   /**
    * Create a multiplexed stream for connecting to an untrusted context like a
    * like a website, Snap, or other extension.
```

### app/scripts/metamask-controller.actions.test.js
```diff
@@ -287,6 +287,33 @@ describe('MetaMaskController', function () {
     });
   });
 
+  describe('#createNewVaultAndGetSeedPhrase', function () {
+    it('creates a vault and returns the seed phrase', async function () {
+      const password = 'test@123';
+      const encodedSeedPhrase =
+        await metamaskController.createNewVaultAndGetSeedPhrase(password);
+      const seedPhrase = Buffer.from(encodedSeedPhrase).toString('utf8');
+
+      expect(seedPhrase.split(' ')).toHaveLength(12);
+      expect(metamaskController.keyringController.state.isUnlocked).toBe(true);
+    });
+  });
+
+  describe('#unlockAndGetSeedPhrase', function () {
+    it('unlocks the vault and returns the seed phrase', async function () {
+      const password = 'test@123';
+      await metamaskController.createNewVaultAndKeychain(password);
+      await metamaskController.keyringController.setLocked();
+
+      const encodedSeedPhrase =
+        await metamaskController.unlockAndGetSeedPhrase(password);
+      const seedPhrase = Buffer.from(encodedSeedPhrase).toString('utf8');
+
+      expect(seedPhrase.split(' ')).toHaveLength(12);
+      expect(metamaskController.keyringController.state.isUnlocked).toBe(true);
+    });
+  });
+
   describe('#addToken', function () {
     const address = '0x514910771af9ca656af840dff83e8264ecf986ca';
     const symbol = 'LINK';
```

### app/scripts/metamask-controller.js
```diff
@@ -3357,6 +3357,9 @@ export default class MetamaskController extends EventEmitter {
         'LegacyBackgroundApiService:setLocked',
       ),
       createNewVaultAndKeychain: this.createNewVaultAndKeychain.bind(this),
+      createNewVaultAndGetSeedPhrase:
+        this.createNewVaultAndGetSeedPhrase.bind(this),
+      unlockAndGetSeedPhrase: this.unlockAndGetSeedPhrase.bind(this),
       createNewVaultAndRestore: this.createNewVaultAndRestore.bind(this),
       importMnemonicToVault: this.importMnemonicToVault.bind(this),
       exportAccount: this.controllerMessenger.call.bind(
@@ -4758,51 +4761,99 @@ export default class MetamaskController extends EventEmitter {
    */
   async createNewVaultAndKeychain(password) {
     const releaseLock = await this.createVaultMutex.acquire();
+    try {
+      return await this._createNewVaultAndKeychainUnderLock(password);
+    } finally {
+      releaseLock();
+    }
+  }
+
+  /**
+   * Creates a new vault and returns the seed phrase in a single atomic operation.
+   * Holding the vault mutex through seed export avoids races where concurrent
+   * keyring mutations leave no HD keyring available for export.
+   *
+   * @param {string} password
+   * @returns {Promise<Buffer>} The seed phrase encoded as UTF-8 bytes.
+   */
+  async createNewVaultAndGetSeedPhrase(password) {
+    const releaseLock = await this.createVaultMutex.acquire();
+    try {
+      await this._createNewVaultAndKeychainUnderLock(password);
+      return await this.controllerMessenger.call(
+        'LegacyBackgroundApiService:getSeedPhrase',
+        password,
+      );
+    } finally {
+      releaseLock();
+    }
+  }
+
+  /**
+   * Unlocks the vault and returns the seed phrase in a single atomic operation.
+   * Holding the vault mutex through seed export avoids races where concurrent
+   * keyring mutations leave no HD keyring available for export.
+   *
+   * @param {string} password
+   * @returns {Promise<Buffer>} The seed phrase encoded as UTF-8 bytes.
+   */
+  async unlockAndGetSeedPhrase(password) {
+    const releaseLock = await this.createVaultMutex.acquire();
+    try {
+      await this.legacyBackgroundApiService.submitPasswordOrEncryptionKey({
+        password,
+      });
+      return await this.controllerMessenger.call(
+        'LegacyBackgroundApiService:getSeedPhrase',
+        password,
+      );
+    } finally {
+      releaseLock();
+    }
+  }
+
+  async _createNewVaultAndKeychainUnderLock(password) {
     const isWalletResetInProgress =
       this.appStateController.getIsWalletResetInProgress();
-    try {
-      if (isWalletResetInProgress) {
-        // clear permissions
-        this.permissionController.clearState();
+    if (isWalletResetInProgress) {
+      // clear permissions
+      this.permissionController.clearState();
 
-        // Clear snap state
-        await this.snapController.clearState();
+      // Clear snap state
+      await this.snapController.clearState();
 
-        // Clear account tree state
-        this.accountTreeController.clearState();
+      // Clear account tree state
+      this.accountTreeController.clearState();
 
-        // Currently, the account-order-controller is not in sync with
-        // the accounts-controller. To properly persist the hidden state
-        // of accounts, we should add a new flag to the account struct
-        // to indicate if it is hidden or not.
-        // TODO: Update @metamask/accounts-controller to support this.
-        this.accountOrderController.updateHiddenAccountsList([]);
+      // Currently, the account-order-controller is not in sync with
+      // the accounts-controller. To properly persist the hidden state
+      // of accounts, we should add a new flag to the account struct
+      // to indicate if it is hidden or not.
+      // TODO: Update @metamask/accounts-controller to support this.
+      this.accountOrderController.updateHiddenAccountsList([]);
 
-        this.txController.clearUnapprovedTransactions();
-      }
+      this.txController.clearUnapprovedTransactions();
+    }
 
-      await this.multichainAccountService.createMultichainAccountWallet({
-        type: 'create',
-        password,
-      });
+    await this.multichainAccountService.createMultichainAccountWallet({
+      type: 'create',
+      password,
+    });
 
-      // set is resetting wallet in progress to false, after new vault and keychain are created
-      this.appStateController.setIsWalletResetInProgress(false);
+    // set is resetting wallet in progress to false, after new vault and keychain are created
+    this.appStateController.setIsWalletResetInProgress(false);
 
-      const primaryKeyring = this.keyringController.state.keyrings[0];
+    const primaryKeyring = this.keyringController.state.keyrings[0];
 
-      // Once we have our first HD keyring available, we re-create the internal list of
-      // accounts (they should be up-to-date already, but we still run `updateAccounts` as
-      // there are some account migration happening in that function).
-      await this.accountsController.updateAccounts();
+    // Once we have our first HD keyring available, we re-create the internal list of
+    // accounts (they should be up-to-date already, but we still run `updateAccounts` as
+    // there are some account migration happening in that function).
+    await this.accountsController.updateAccounts();
 
-      // Then we can build the initial tree.
-      this.accountTreeController.reinit();
+    // Then we can build the initial tree.
+    this.accountTreeController.reinit();
 
-      return primaryKeyring;
-    } finally {
-      releaseLock();
-    }
+    return primaryKeyring;
   }
 
   /**
@@ -9115,6 +9166,7 @@ export default class MetamaskController extends EventEmitter {
       // migrate the seedless onboarding functionality to the LegacyBackgroundApiService.
       // TODO: Remove this once the migration is complete.
       seedlessOperationMutex: this.seedlessOperationMutex,
+      createVaultMutex: this.createVaultMutex,
       setupUntrustedCommunicationEip1193:
         this.setupUntrustedCommunicationEip1193.bind(this),
       setupUntrustedCommunicationCaip:
```

### app/scripts/services/legacy-background-api-service.test.ts
```diff
@@ -3645,6 +3645,7 @@ async function withService<ReturnValue>(
     getOpenMetamaskTabsIds: () => ({}),
     sendUpdate: jest.fn(),
     seedlessOperationMutex: new Mutex(),
+    createVaultMutex: new Mutex(),
     offscreenPromise: Promise.resolve(),
     ...options,
   });
```

### app/scripts/services/legacy-background-api-service.ts
```diff
@@ -349,6 +349,7 @@ type LegacyBackgroundApiServiceOptions = {
   messenger: LegacyBackgroundApiServiceMessenger;
   infuraProjectId: string;
   seedlessOperationMutex: Mutex;
+  createVaultMutex: Mutex;
   getRequestAccountTabIds: () => Record<string, number>;
   getOpenMetamaskTabsIds: () => Record<string, number>;
   sendUpdate: () => void;
@@ -379,6 +380,8 @@ export class LegacyBackgroundApiService {
 
   readonly #seedlessOperationMutex: Mutex;
 
+  readonly #createVaultMutex: Mutex;
+
   readonly #offscreenPromise: Promise<void>;
 
   #passkeyAutoUnlockSuppressedResetTimeoutId: NodeJS.Timeout | null = null;
@@ -392,6 +395,7 @@ export class LegacyBackgroundApiService {
    * @param options.getOpenMetamaskTabsIds - A function that returns a record of open MetaMask tab IDs.
    * @param options.sendUpdate - A function that triggers an update to the UI.
    * @param options.seedlessOperationMutex - A mutex to use for seedless operations.
+   * @param options.createVaultMutex - A mutex to serialize vault creation/export with locking.
    * @param options.offscreenPromise - A promise that resolves when the offscreen document is ready.
    */
   constructor({
@@ -401,6 +405,7 @@ export class LegacyBackgroundApiService {
     getOpenMetamaskTabsIds,
     sendUpdate,
     seedlessOperationMutex,
+    createVaultMutex,
     offscreenPromise,
   }: LegacyBackgroundApiServiceOptions) {
     this.#messenger = messenger;
@@ -413,6 +418,7 @@ export class LegacyBackgroundApiService {
     // migrate the seedless onboarding functionality to this service.
     // TODO: Remove this once the migration is complete.
     this.#seedlessOperationMutex = seedlessOperationMutex;
+    this.#createVaultMutex = createVaultMutex;
     this.#offscreenPromise = offscreenPromise;
 
     this.#messenger.registerMethodActionHandlers(
@@ -1343,57 +1349,62 @@ export class LegacyBackgroundApiService {
    * @param options.skipSeedlessOperationLock - If true, the seedless operation mutex will not be locked.
    */
   async setLocked({ skipSeedlessOperationLock = false } = {}): Promise<void> {
-    const isSocialLoginFlow = this.#messenger.call(
-      'OnboardingController:getIsSocialLoginFlow',
-    );
-
-    let releaseLock;
-    if (isSocialLoginFlow && !skipSeedlessOperationLock) {
-      releaseLock = await this.#seedlessOperationMutex.acquire();
-    }
-
+    const releaseVaultMutex = await this.#createVaultMutex.acquire();
     try {
-      if (isSocialLoginFlow) {
-        await this.#messenger.call('SeedlessOnboardingController:setLocked');
+      const isSocialLoginFlow = this.#messenger.call(
+        'OnboardingController:getIsSocialLoginFlow',
+      );
+
+      let releaseLock;
+      if (isSocialLoginFlow && !skipSeedlessOperationLock) {
+        releaseLock = await this.#seedlessOperationMutex.acquire();
       }
-      await this.#messenger.call('KeyringController:setLocked');
 
-      // stop polling for the subscriptions when the wallet is locked manually and window/side-panel is still open
-      this.#messenger.call('SubscriptionController:stopAllPolling');
+      try {
+        if (isSocialLoginFlow) {
+          await this.#messenger.call('SeedlessOnboardingController:setLocked');
+        }
+        await this.#messenger.call('KeyringController:setLocked');
 
-      // sign out from Authentication service and clear the Session Data if user is signed in
-      // this check is to make sure that the user sensitive data is cleared when the wallet is locked.
-      // We have `useAutoSignOut` hook that should handle the automatic sign out, however, it's not always triggered.
-      const { isSignedIn } = this.#messenger.call(
-        'AuthenticationController:getState',
-      );
-      if (isSignedIn) {
-        this.#messenger.call('AuthenticationController:performSignOut');
-      }
+        // stop polling for the subscriptions when the wallet is locked manually and window/side-panel is still open
+        this.#messenger.call('SubscriptionController:stopAllPolling');
 
-      // After lock, suppress auto passkey unlock briefly (cross-surface), then clear.
-      if (this.#passkeyAutoUnlockSuppressedResetTimeoutId !== null) {
-        clearTimeout(this.#passkeyAutoUnlockSuppressedResetTimeoutId);
-        this.#passkeyAutoUnlockSuppressedResetTimeoutId = null;
-      }
-      this.#messenger.call(
-        'AppStateController:setPasskeyAutoUnlockSuppressed',
-        true,
-      );
-      this.#passkeyAutoUnlockSuppressedResetTimeoutId = setTimeout(() => {
-        this.#passkeyAutoUnlockSuppressedResetTimeoutId = null;
+        // sign out from Authentication service and clear the Session Data if user is signed in
+        // this check is to make sure that the user sensitive data is cleared when the wallet is locked.
+        // We have `useAutoSignOut` hook that should handle the automatic sign out, however, it's not always triggered.
+        const { isSignedIn } = this.#messenger.call(
+          'AuthenticationController:getState',
+        );
+        if (isSignedIn) {
+          this.#messenger.call('AuthenticationController:performSignOut');
+        }
+
+        // After lock, suppress auto passkey unlock briefly (cross-surface), then clear.
+        if (this.#passkeyAutoUnlockSuppressedResetTimeoutId !== null) {
+          clearTimeout(this.#passkeyAutoUnlockSuppressedResetTimeoutId);
+          this.#passkeyAutoUnlockSuppressedResetTimeoutId = null;
+        }
         this.#messenger.call(
           'AppStateController:setPasskeyAutoUnlockSuppressed',
-          false,
+          true,
         );
-      }, PASSKEY_AUTO_UNLOCK_SUPPRESSION_DURATION_MS);
-    } catch (error) {
-      log.error('Error setting locked state', error);
-      throw error;
-    } finally {
-      if (releaseLock) {
-        releaseLock();
+        this.#passkeyAutoUnlockSuppressedResetTimeoutId = setTimeout(() => {
+          this.#passkeyAutoUnlockSuppressedResetTimeoutId = null;
+          this.#messenger.call(
+            'AppStateController:setPasskeyAutoUnlockSuppressed',
+            false,
+          );
+        }, PASSKEY_AUTO_UNLOCK_SUPPRESSION_DURATION_MS);
+      } catch (error) {
+        log.error('Error setting locked state', error);
+        throw error;
+      } finally {
+        if (releaseLock) {
+          releaseLock();
+        }
       }
+    } finally {
+      releaseVaultMutex();
     }
   }
 
```

### ui/hooks/useCloseSidePanelOnWalletReset.test.ts
```diff
@@ -0,0 +1,54 @@
+import {
+  ENVIRONMENT_TYPE_POPUP,
+  ENVIRONMENT_TYPE_SIDEPANEL,
+} from '../../shared/constants/app';
+import { getEnvironmentType } from '../../shared/lib/environment-type';
+import { renderHookWithProvider } from '../../test/lib/render-helpers-navigate';
+import { useCloseSidePanelOnWalletReset } from './useCloseSidePanelOnWalletReset';
+
+jest.mock('../../shared/lib/environment-type', () => ({
+  ...jest.requireActual('../../shared/lib/environment-type'),
+  getEnvironmentType: jest.fn(),
+}));
+
+const mockGetEnvironmentType = jest.mocked(getEnvironmentType);
+
+describe('useCloseSidePanelOnWalletReset', () => {
+  let closeSpy: jest.SpyInstance;
+
+  beforeEach(() => {
+    closeSpy = jest.spyOn(window, 'close').mockImplementation(() => undefined);
+    mockGetEnvironmentType.mockReturnValue(ENVIRONMENT_TYPE_SIDEPANEL);
+  });
+
+  afterEach(() => {
+    closeSpy.mockRestore();
+    jest.clearAllMocks();
+  });
+
+  it('closes the side panel when wallet reset is in progress', () => {
+    renderHookWithProvider(() => useCloseSidePanelOnWalletReset(), {
+      metamask: { isWalletResetInProgress: true },
+    });
+
+    expect(closeSpy).toHaveBeenCalledTimes(1);
+  });
+
+  it('does not close when wallet reset is not in progress', () => {
+    renderHookWithProvider(() => useCloseSidePanelOnWalletReset(), {
+      metamask: { isWalletResetInProgress: false },
+    });
+
+    expect(closeSpy).not.toHaveBeenCalled();
+  });
+
+  it('does not close outside the side panel', () => {
+    mockGetEnvironmentType.mockReturnValue(ENVIRONMENT_TYPE_POPUP);
+
+    renderHookWithProvider(() => useCloseSidePanelOnWalletReset(), {
+      metamask: { isWalletResetInProgress: true },
+    });
+
+    expect(closeSpy).not.toHaveBeenCalled();
+  });
+});
```

### ui/hooks/useCloseSidePanelOnWalletReset.ts
```diff
@@ -0,0 +1,24 @@
+import { useEffect } from 'react';
+import { useSelector } from 'react-redux';
+import { ENVIRONMENT_TYPE_SIDEPANEL } from '../../shared/constants/app';
+import { getEnvironmentType } from '../../shared/lib/environment-type';
+import { getIsWalletResetInProgress } from '../ducks/metamask/metamask';
+
+/**
+ * Closes the side panel when a wallet reset is in progress and the wallet
+ * becomes unlocked on another MetaMask surface. The side panel keeps its own
+ * Redux store, so an unlocked-but-not-onboarded panel can race second-pass
+ * onboarding and trigger the onboarding lock trap.
+ */
+export function useCloseSidePanelOnWalletReset(): void {
+  const isWalletResetInProgress = useSelector(getIsWalletResetInProgress);
+
+  useEffect(() => {
+    if (
+      getEnvironmentType() === ENVIRONMENT_TYPE_SIDEPANEL &&
+      isWalletResetInProgress
+    ) {
+      window.close();
+    }
+  }, [isWalletResetInProgress]);
+}
```

### ui/pages/onboarding-flow/create-password/create-password.test.tsx
```diff
@@ -392,7 +392,7 @@ describe('Onboarding Create Password', () => {
       expect(mockCreateNewAccount).not.toHaveBeenCalled();
     });
 
-    it('should create new wallet without marketing checked when its social login flow', () => {
+    it('should create new wallet without marketing checked when its social login flow', async () => {
       const mockStore = configureMockStore([thunk])({
         ...mockState,
         metamask: {
@@ -441,7 +441,9 @@ describe('Onboarding Create Password', () => {
 
       fireEvent.click(createNewWalletButton as HTMLElement);
 
-      expect(mockCreateNewAccount).toHaveBeenCalled();
+      await waitFor(() => {
+        expect(mockCreateNewAccount).toHaveBeenCalled();
+      });
     });
   });
 
```

### ui/pages/onboarding-flow/create-password/create-password.tsx
```diff
@@ -61,6 +61,7 @@ export default function CreatePassword({
 }: CreatePasswordProps) {
   const [newAccountCreationInProgress, setNewAccountCreationInProgress] =
     useState(false);
+  const [isSubmitting, setIsSubmitting] = useState(false);
   const navigate = useNavigate();
   const dispatch = useDispatch();
   const isFirefox = useIsFirefox();
@@ -316,10 +317,11 @@ export default function CreatePassword({
     password: string,
     termsChecked: boolean,
   ) => {
-    if (!password) {
+    if (!password || isSubmitting) {
       return;
     }
 
+    setIsSubmitting(true);
     try {
       // If secretRecoveryPhrase is defined we are in import wallet flow
       if (
@@ -339,6 +341,9 @@ export default function CreatePassword({
           .addCategory(MetaMetricsEventCategory.Onboarding)
           .build(),
       );
+      setNewAccountCreationInProgress(false);
+    } finally {
+      setIsSubmitting(false);
     }
   };
 
@@ -348,6 +353,7 @@ export default function CreatePassword({
         isSocialLoginFlow={isSocialLoginFlow}
         onSubmit={handleCreatePassword}
         onBack={handleBackClick}
+        loading={isSubmitting}
       />
       {shouldInjectMetametricsIframe ? (
         <iframe
```

### ui/pages/routes/routes.component.tsx
```diff
@@ -124,6 +124,7 @@ import { MultichainAccountAddressListPage } from '../multichain-accounts/multich
 import { MultichainAccountPrivateKeyListPage } from '../multichain-accounts/multichain-account-private-key-list-page';
 import MultichainAccountIntroModalContainer from '../../components/app/modals/multichain-accounts/intro-modal';
 import { useMultichainAccountsIntroModal } from '../../hooks/useMultichainAccountsIntroModal';
+import { useCloseSidePanelOnWalletReset } from '../../hooks/useCloseSidePanelOnWalletReset';
 import { useSpinDelay } from '../../hooks/useSpinDelay';
 import { AccountList } from '../multichain-accounts/account-list';
 import { AddWalletPage } from '../multichain-accounts/add-wallet-page';
@@ -640,6 +641,12 @@ export default function Routes() {
   const { showMultichainIntroModal, setShowMultichainIntroModal } =
     useMultichainAccountsIntroModal(isUnlocked, location);
 
+  // Close the side panel when a wallet reset is in progress and the wallet
+  // becomes unlocked on another MetaMask surface. The side panel keeps its own
+  // Redux store, so an unlocked-but-not-onboarded panel can race second-pass
+  // onboarding and trigger the onboarding lock trap.
+  useCloseSidePanelOnWalletReset();
+
   const isUsingRedesignedConfirmationType = useIsRedesignedConfirmationType();
 
   useEffect(() => {
```
