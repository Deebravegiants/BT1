# [?] fix(bridge-ui): show quota exhaustion claim error (#21903)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2026-07-03
Source: https://github.com/taikoxyz/taiko-mono/commit/d92e7a81f582c6438b6313826d3bc14a1b7abb11
Type: security-commit

## Details
fix(bridge-ui): show quota exhaustion claim error (#21903)

Co-authored-by: Gustavo Gonzalez <gustavo@taiko.xyz>

## Patch
### packages/bridge-ui/src/components/Dialogs/ClaimDialog/ClaimDialog.svelte
```diff
@@ -33,7 +33,7 @@
   import { ClaimAction } from '../Shared/types';
   import { DialogStep, DialogStepper } from '../Stepper';
   import ClaimStepNavigation from './ClaimStepNavigation.svelte';
-  import { isMessageNotReceivedError } from './error';
+  import { isMessageNotReceivedError, isQuotaManagerOutOfQuotaError } from './error';
   import { type ClaimDialogMode, shouldSkipMessageStatusCheck } from './mode';
   import { ClaimSteps, INITIAL_STEP } from './types';
 
@@ -155,6 +155,11 @@
             title: $t('bridge.errors.claim.not_received.title'),
             message: $t('bridge.errors.claim.not_received.message'),
           });
+        } else if (isQuotaManagerOutOfQuotaError(err)) {
+          errorToast({
+            title: $t('bridge.errors.claim.quota_reached.title'),
+            message: $t('bridge.errors.claim.quota_reached.message'),
+          });
         } else {
           errorToast({
             title: $t('bridge.errors.unknown_error.title'),
```

### packages/bridge-ui/src/components/Dialogs/ClaimDialog/error.test.ts
```diff
@@ -1,6 +1,6 @@
 import { describe, expect, it } from 'vitest';
 
-import { isMessageNotReceivedError } from './error';
+import { isMessageNotReceivedError, isQuotaManagerOutOfQuotaError } from './error';
 
 describe('isMessageNotReceivedError', () => {
   it('returns true for legacy and current bridge not received errors', () => {
@@ -26,3 +26,46 @@ describe('isMessageNotReceivedError', () => {
     expect(isMessageNotReceivedError(new Error('execution reverted: B_PERMISSION_DENIED()'))).toBe(false);
   });
 });
+
+describe('isQuotaManagerOutOfQuotaError', () => {
+  it('returns true when viem decodes the quota manager custom error name', () => {
+    const wrappedError = {
+      message: 'The contract function "processMessage" reverted.',
+      cause: {
+        shortMessage: 'The contract function reverted.',
+        data: {
+          errorName: 'QM_OUT_OF_QUOTA',
+        },
+      },
+    };
+
+    expect(isQuotaManagerOutOfQuotaError(wrappedError)).toBe(true);
+  });
+
+  it('returns true when viem cannot decode the custom error but includes its selector', () => {
+    const wrappedError = {
+      message: 'The contract function "processMessage" reverted.',
+      cause: {
+        shortMessage: 'Encoded error signature "0x51d8fe3a" not found on ABI.',
+        data: '0x51d8fe3a',
+      },
+    };
+
+    expect(isQuotaManagerOutOfQuotaError(wrappedError)).toBe(true);
+  });
+
+  it('returns true when viem exposes only the custom error signature field', () => {
+    const wrappedError = {
+      message: 'The contract function "processMessage" reverted.',
+      cause: {
+        signature: '0x51d8fe3a',
+      },
+    };
+
+    expect(isQuotaManagerOutOfQuotaError(wrappedError)).toBe(true);
+  });
+
+  it('returns false for unrelated quota manager errors', () => {
+    expect(isQuotaManagerOutOfQuotaError(new Error('execution reverted: QM_INVALID_PARAM()'))).toBe(false);
+  });
+});
```

### packages/bridge-ui/src/components/Dialogs/ClaimDialog/error.ts
```diff
@@ -1,4 +1,5 @@
 const MESSAGE_NOT_RECEIVED_ERRORS = ['B_NOT_RECEIVED', 'B_SIGNAL_NOT_RECEIVED'];
+const QUOTA_MANAGER_OUT_OF_QUOTA_ERRORS = ['QM_OUT_OF_QUOTA', '0x51d8fe3a'];
 
 function collectErrorTexts(error: unknown): string[] {
   if (!error || typeof error !== 'object') {
@@ -10,6 +11,8 @@ function collectErrorTexts(error: unknown): string[] {
     shortMessage?: unknown;
     details?: unknown;
     reason?: unknown;
+    signature?: unknown;
+    metaMessages?: unknown;
     data?: { errorName?: unknown } | unknown;
     cause?: unknown;
   };
@@ -19,6 +22,9 @@ function collectErrorTexts(error: unknown): string[] {
     maybeError.shortMessage,
     maybeError.details,
     maybeError.reason,
+    maybeError.signature,
+    ...(Array.isArray(maybeError.metaMessages) ? maybeError.metaMessages : []),
+    typeof maybeError.data === 'string' ? maybeError.data : undefined,
     typeof maybeError.data === 'object' && maybeError.data && 'errorName' in maybeError.data
       ? maybeError.data.errorName
       : undefined,
@@ -31,3 +37,8 @@ export function isMessageNotReceivedError(error: unknown): boolean {
   const haystacks = collectErrorTexts(error);
   return haystacks.some((text) => MESSAGE_NOT_RECEIVED_ERRORS.some((needle) => text.includes(needle)));
 }
+
+export function isQuotaManagerOutOfQuotaError(error: unknown): boolean {
+  const haystacks = collectErrorTexts(error);
+  return haystacks.some((text) => QUOTA_MANAGER_OUT_OF_QUOTA_ERRORS.some((needle) => text.includes(needle)));
+}
```

### packages/bridge-ui/src/i18n/en.json
```diff
@@ -85,6 +85,10 @@
         "not_received": {
           "message": "The message is not proven and cannot be claimed right now.",
           "title": "Not received"
+        },
+        "quota_reached": {
+          "message": "This asset's withdrawal quota is currently used up. Your funds are safe; wait for the quota to replenish, then try claiming again.",
+          "title": "Withdrawal quota reached"
         }
       },
       "custom_token": {
```
