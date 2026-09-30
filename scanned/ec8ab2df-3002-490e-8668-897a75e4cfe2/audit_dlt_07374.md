# [?] release(runway): cherry-pick fix: Prevent crash in modal version handling cp-13.11.1 (#38396)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2025-11-28
Source: https://github.com/MetaMask/metamask-extension/commit/86ef0b6ca9762d4cfc706daeb501329aa081eac6
Type: security-commit

## Details
release(runway): cherry-pick fix: Prevent crash in modal version handling cp-13.11.1 (#38396)

- fix: Prevent crash in modal version handling cp-13.11.1 (#38382)

<!--
Please submit this PR as a draft initially.
Do not mark it as "Ready for review" until the template has been
completely filled out, and PR status checks have passed at least once.
-->

## **Description**

Fixes a crash caused by `useMultichainAccountsIntroModal` that entirely
bricks Flask. The crash occurs because the version handling doesn't
handle our versioning scheme well. This PR changes the logic to use
`previousAppVersion` and strips the `prerelease` part of the version
(which indicates the build type) for a proper comparison.

Also updates the tests for this hook which were flawed as they didn't
use the hook in question at all.

[![Open in GitHub

Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MetaMask/metamask-extension/pull/38382?quickstart=1)

## **Changelog**

<!--
If this PR is not End-User-Facing and should not show up in the
CHANGELOG, you can choose to either:
1. Write `CHANGELOG entry: null`
2. Label with `no-changelog`

If this PR is End-User-Facing, please write a short User-Facing
description in the past tense like:
`CHANGELOG entry: Added a new tab for users to see their NFTs`
`CHANGELOG entry: Fixed a bug that was causing some NFTs to flicker`

(This helps the Release Engineer do their job more quickly and
accurately)
-->

CHANGELOG entry: Fixes a crash when updating Flask

## **Manual testing steps**

1. Force `lastUpdatedFromVersion` to `13.9.0.150` and
`previousAppVersion` to `13.9.0-flask.0`
2. See that it crashes without this PR

## **Screenshots/Recordings**

<!-- If applicable, add screenshots and/or recordings to visualize the
before and after of your change. -->

### **Before**

<img width="454" height="634" alt="image"

src="https://github.com/user-attachments/assets/ea140cfa-66ef-402e-a6cd-3ca3a2bc6402"
/>


<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Fixes modal logic by parsing/stripping prerelease versions and using
`previousAppVersion`, preventing crashes; rewrites tests to exercise the
hook with provider-backed state.
> 
> - **Hook (`ui/hooks/useMultichainAccountsIntroModal.ts`)**:
> - Export `BIP44_ACCOUNTS_INTRODUCTION_VERSION` and switch version
source to `state.metamask.previousAppVersion`.
> - Parse versions with `semver.parse` and strip prerelease before
comparing with `semver.lt`.
> - Maintain display conditions (unlocked, feature flag, not previously
shown, upgrade, main route) and set `showMultichainIntroModal`
accordingly.
> - **Tests (`ui/hooks/useMultichainAccountsIntroModal.test.ts`)**:
> - Replace standalone logic tests with `renderHookWithProvider` to test
the actual hook.
> - Add cases for prerelease versions (e.g., `13.4.0-flask.0`) and
threshold boundaries; verify behavior across route, lock state, feature
flag, prior display, and fresh install.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
a46d32a4b3e44f20220c31b58e28b460aa024e0c. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->


[a3c1ac2](https://github.com/MetaMask/metamask-extension/commit/a3c1ac2baa163bdef59c5289dc93ccca786b38b8)

Co-authored-by: Frederik Bolding <frederik.bolding@gmail.com>

## Patch
### ui/hooks/useMultichainAccountsIntroModal.test.ts
```diff
@@ -1,31 +1,34 @@
-import { lt as semverLt } from 'semver';
+import { renderHookWithProvider } from '../../test/lib/render-helpers';
+import {
+  useMultichainAccountsIntroModal,
+  BIP44_ACCOUNTS_INTRODUCTION_VERSION,
+} from './useMultichainAccountsIntroModal';
 
-// Test the core logic independently of React hooks
-describe('BIP-44 Banner Logic', () => {
-  const BIP44_ACCOUNTS_INTRODUCTION_VERSION = '13.5.0';
-
-  // Helper function that mirrors the hook's core logic
-  const shouldShowBip44Banner = (
+describe('useMultichainAccountsIntroModal', () => {
+  const renderHook = (
     isUnlocked: boolean,
     isMultichainAccountsEnabled: boolean,
-    hasShownModalBefore: boolean,
+    hasShownMultichainAccountsIntroModal: boolean,
     lastUpdatedAt: number | null,
-    lastUpdatedFromVersion: string | null,
-    isMainRoute: boolean,
+    previousAppVersion: string | null,
+    pathname: string,
   ) => {
-    const isUpgradeFromLowerThanBip44Version = Boolean(
-      lastUpdatedFromVersion &&
-        typeof lastUpdatedFromVersion === 'string' &&
-        semverLt(lastUpdatedFromVersion, BIP44_ACCOUNTS_INTRODUCTION_VERSION),
-    );
-
-    return (
-      isUnlocked &&
-      isMultichainAccountsEnabled &&
-      !hasShownModalBefore &&
-      lastUpdatedAt !== null && // null = fresh install, timestamp = upgrade
-      isUpgradeFromLowerThanBip44Version &&
-      isMainRoute
+    return renderHookWithProvider(
+      () => useMultichainAccountsIntroModal(isUnlocked, { pathname }),
+      {
+        metamask: {
+          remoteFeatureFlags: {
+            enableMultichainAccountsState2: {
+              enabled: isMultichainAccountsEnabled,
+              featureVersion: '2',
+              minimumVersion: BIP44_ACCOUNTS_INTRODUCTION_VERSION,
+            },
+          },
+          hasShownMultichainAccountsIntroModal,
+          previousAppVersion,
+          lastUpdatedAt,
+        },
+      },
     );
   };
 
@@ -39,137 +42,147 @@ describe('BIP-44 Banner Logic', () => {
     };
 
     it('shows banner for upgrade from 13.4.0', () => {
-      const result = shouldShowBip44Banner(
+      const { result } = renderHook(
         baseParams.isUnlocked,
         baseParams.isMultichainAccountsEnabled,
         baseParams.hasShownModalBefore,
         baseParams.lastUpdatedAt,
         '13.4.0',
-        baseParams.isMainRoute,
+        '/',
       );
-      expect(result).toBe(true);
+      expect(result.current.showMultichainIntroModal).toBe(true);
+    });
+
+    it('shows banner for upgrade from 13.4.0-flask.0', () => {
+      const { result } = renderHook(
+        baseParams.isUnlocked,
+        baseParams.isMultichainAccountsEnabled,
+        baseParams.hasShownModalBefore,
+        baseParams.lastUpdatedAt,
+        '13.4.0-flask.0',
+        '/',
+      );
+      expect(result.current.showMultichainIntroModal).toBe(true);
     });
 
     it('shows banner for upgrade from 12.0.0', () => {
-      const result = shouldShowBip44Banner(
+      const { result } = renderHook(
         true,
         true,
         false,
         Date.now(),
         '12.0.0',
-        true,
+        '/',
       );
-      expect(result).toBe(true);
+      expect(result.current.showMultichainIntroModal).toBe(true);
     });
 
     it('shows banner for upgrade from 13.4.9 (just before threshold)', () => {
-      const result = shouldShowBip44Banner(
+      const { result } = renderHook(
         true,
         true,
         false,
         Date.now(),
         '13.4.9',
-        true,
+        '/',
       );
-      expect(result).toBe(true);
+      expect(result.current.showMultichainIntroModal).toBe(true);
     });
   });
 
   describe('does NOT show banner correctly', () => {
     it('does NOT show for upgrade from 13.5.0 (threshold version)', () => {
-      const result = shouldShowBip44Banner(
+      const { result } = renderHook(
         true,
         true,
         false,
         Date.now(),
         '13.5.0',
-        true,
+        '/',
       );
-      expect(result).toBe(false);
+      expect(result.current.showMultichainIntroModal).toBe(false);
     });
 
-    it('does NOT show for upgrade from 13.7.0', () => {
-      const result = shouldShowBip44Banner(
+    it('does NOT show for upgrade from 13.5.0-flask.0 (threshold version)', () => {
+      const { result } = renderHook(
         true,
         true,
         false,
         Date.now(),
-        '13.7.0',
-        true,
+        '13.5.0-flask.0',
+        '/',
       );
-      expect(result).toBe(false);
+      expect(result.current.showMultichainIntroModal).toBe(false);
     });
 
-    it('does NOT show for fresh install (no previous version)', () => {
-      const result = shouldShowBip44Banner(
+    it('does NOT show for upgrade from 13.7.0', () => {
+      const { result } = renderHook(
         true,
         true,
         false,
         Date.now(),
-        null,
-        true,
+        '13.7.0',
+        '/',
       );
-      expect(result).toBe(false);
+      expect(result.current.showMultichainIntroModal).toBe(false);
+    });
+
+    it('does NOT show for fresh install (no previous version)', () => {
+      const { result } = renderHook(true, true, false, Date.now(), null, '/');
+      expect(result.current.showMultichainIntroModal).toBe(false);
     });
 
     it('does NOT show when wallet is locked', () => {
-      const result = shouldShowBip44Banner(
+      const { result } = renderHook(
         false,
         true,
         false,
         Date.now(),
         '13.4.0',
-        true,
+        '/',
       );
-      expect(result).toBe(false);
+      expect(result.current.showMultichainIntroModal).toBe(false);
     });
 
     it('does NOT show when multichain accounts disabled', () => {
-      const result = shouldShowBip44Banner(
+      const { result } = renderHook(
         true,
         false,
         false,
         Date.now(),
         '13.4.0',
-        true,
+        '/',
       );
-      expect(result).toBe(false);
+      expect(result.current.showMultichainIntroModal).toBe(false);
     });
 
     it('does NOT show when modal already shown', () => {
-      const result = shouldShowBip44Banner(
+      const { result } = renderHook(
         true,
         true,
         true,
         Date.now(),
         '13.4.0',
-        true,
+        '/',
       );
-      expect(result).toBe(false);
+      expect(result.current.showMultichainIntroModal).toBe(false);
     });
 
     it('does NOT show on non-main route', () => {
-      const result = shouldShowBip44Banner(
+      const { result } = renderHook(
         true,
         true,
         false,
         Date.now(),
         '13.4.0',
-        false,
+        '/confirmation/foo',
       );
-      expect(result).toBe(false);
+      expect(result.current.showMultichainIntroModal).toBe(false);
     });
 
     it('does NOT show for fresh install (lastUpdatedAt is null)', () => {
-      const result = shouldShowBip44Banner(
-        true,
-        true,
-        false,
-        null,
-        '13.4.0',
-        true,
-      );
-      expect(result).toBe(false);
+      const { result } = renderHook(true, true, false, null, '13.4.0', '/');
+      expect(result.current.showMultichainIntroModal).toBe(false);
     });
   });
 });
```

### ui/hooks/useMultichainAccountsIntroModal.ts
```diff
@@ -1,12 +1,11 @@
 import { useState, useEffect } from 'react';
-import { lt as semverLt } from 'semver';
+import { lt as semverLt, parse as semverParse } from 'semver';
 import { useAppSelector } from '../store/store';
 import { getIsMultichainAccountsState2Enabled } from '../selectors/multichain-accounts/feature-flags';
-import { getLastUpdatedFromVersion } from '../selectors/selectors';
 import { DEFAULT_ROUTE } from '../helpers/constants/routes';
 
 // Version threshold for BIP-44 multichain accounts introduction
-const BIP44_ACCOUNTS_INTRODUCTION_VERSION = '13.5.0';
+export const BIP44_ACCOUNTS_INTRODUCTION_VERSION = '13.5.0';
 
 /**
  * Hook to manage the multichain accounts intro modal display logic
@@ -33,17 +32,24 @@ export function useMultichainAccountsIntroModal(
   );
 
   const lastUpdatedAt = useAppSelector((state) => state.metamask.lastUpdatedAt);
-  const lastUpdatedFromVersion = useAppSelector(getLastUpdatedFromVersion);
+  const lastUpdatedFromVersion = useAppSelector(
+    (state) => state.metamask.previousAppVersion,
+  );
 
   useEffect(() => {
     // Only show modal on the main wallet/home route
     const isMainWalletArea = location.pathname === DEFAULT_ROUTE;
 
+    const parsedLastVersion = semverParse(lastUpdatedFromVersion);
+    // Strip prerelease versions as they just indicate build types.
+    const strippedLastVersion = parsedLastVersion
+      ? `${parsedLastVersion.major}.${parsedLastVersion.minor}.${parsedLastVersion.patch}`
+      : null;
+
     // Check if this is an upgrade from a version lower than BIP-44 introduction version
     const isUpgradeFromLowerThanBip44Version = Boolean(
-      lastUpdatedFromVersion &&
-        typeof lastUpdatedFromVersion === 'string' &&
-        semverLt(lastUpdatedFromVersion, BIP44_ACCOUNTS_INTRODUCTION_VERSION),
+      strippedLastVersion &&
+        semverLt(strippedLastVersion, BIP44_ACCOUNTS_INTRODUCTION_VERSION),
     );
 
     // Show modal only for upgrades from versions < BIP-44 introduction version
```
