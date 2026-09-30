# [?] fix: profile sync controller - prevent infinite crashes. (#4533)

## Summary
Severity: Unknown
Chain: Tooling
Component: MetaMask/core
Published: 2024-07-18
Source: https://github.com/MetaMask/core/commit/db8774cb7651536870d2071ffcfbdbb7aeb61582
Type: security-commit

## Details
fix: profile sync controller - prevent infinite crashes. (#4533)

## Explanation

This is an interested bug that happens through communications with our
controllers.

1. If authentication fails, we call "disable profile syncing"
2. This "disable profile syncing" will make calls to our "notification
services controller"
3. The notification services controller relies on auth, so if auth
continues to fail then we have a loop.

We are now removing the call to "disable profile syncing", and instead
this will be used in the UI or called in a different area. CC
@matteoscurati

## References

[NOTIFY-861](https://consensyssoftware.atlassian.net/browse/NOTIFY-861)

## Changelog

### `@metamask/profile-sync-controller`

- **REMOVED**: Removed internal calls to
`UserStorageController:disableProfileSyncing`.

## Checklist

- [x] I've updated the test suite for new or updated code as appropriate
- [x] I've updated documentation (JSDoc, Markdown, etc.) for new or
updated code as appropriate
- [x] I've highlighted breaking changes using the "BREAKING" category
above as appropriate

## Patch
### packages/profile-sync-controller/src/controllers/authentication/AuthenticationController.test.ts
```diff
@@ -10,6 +10,7 @@ import {
   mockEndpointLogin,
 } from './__fixtures__/mockServices';
 import type {
+  Actions,
   AllowedActions,
   AuthenticationControllerState,
 } from './AuthenticationController';
@@ -271,7 +272,7 @@ describe('authentication/authentication-controller - getSessionProfile() tests',
  * @returns Auth Messenger
  */
 function createAuthenticationMessenger() {
-  const messenger = new ControllerMessenger<AllowedActions, never>();
+  const messenger = new ControllerMessenger<Actions | AllowedActions, never>();
   return messenger.getRestricted({
     name: 'AuthenticationController',
     allowedActions: [`SnapController:handleRequest`],
@@ -310,13 +311,9 @@ function createMockAuthenticationMessenger() {
       );
     }
 
-    const exhaustedMessengerMocks = (action: never) => {
-      throw new Error(
-        `MOCK_FAIL - unsupported messenger call: ${action as string}`,
-      );
-    };
-
-    return exhaustedMessengerMocks(actionType);
+    throw new Error(
+      `MOCK_FAIL - unsupported messenger call: ${actionType as string}`,
+    );
   });
 
   return { messenger, mockSnapGetPublicKey, mockSnapSignMessage };
```

### packages/profile-sync-controller/src/controllers/authentication/AuthenticationController.ts
```diff
@@ -5,7 +5,6 @@ import type {
 import { BaseController } from '@metamask/base-controller';
 import type { HandleSnapRequest } from '@metamask/snaps-controllers';
 
-import type { UserStorageControllerDisableProfileSyncing } from '../user-storage/UserStorageController';
 import {
   createSnapPublicKeyRequest,
   createSnapSignMessageRequest,
@@ -88,9 +87,7 @@ export type AuthenticationControllerGetSessionProfile =
 export type AuthenticationControllerIsSignedIn = ActionsObj['isSignedIn'];
 
 // Allowed Actions
-export type AllowedActions =
-  | HandleSnapRequest
-  | UserStorageControllerDisableProfileSyncing;
+export type AllowedActions = HandleSnapRequest;
 
 // Messenger
 export type AuthenticationControllerMessenger = RestrictedControllerMessenger<
@@ -281,10 +278,6 @@ export default class AuthenticationController extends BaseController<
       };
     } catch (e) {
       console.error('Failed to authenticate', e);
-      // Disable Profile Syncing
-      await this.messagingSystem.call(
-        'UserStorageController:disableProfileSyncing',
-      );
       const errorMessage =
         e instanceof Error ? e.message : JSON.stringify(e ?? '');
       throw new Error(
```
