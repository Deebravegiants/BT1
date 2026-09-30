# [?] fix(wallet, dapp-kit): overflow issues with small screens (#5918)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-03-14
Source: https://github.com/iotaledger/iota/commit/b06e657daea2f2b68ee7025b608a9ad593f32041
Type: security-commit

## Details
fix(wallet, dapp-kit): overflow issues with small screens (#5918)

* fix: overflow issues with small screens

* fix: dialog and add changeset

* fix: improve styles for dialog

---------

Co-authored-by: evavirseda <evirseda@boxfish.studio>

## Patch
### .changeset/fair-tomatoes-remain.md
```diff
@@ -0,0 +1,6 @@
+---
+'@iota/dapp-kit': patch
+'@iota/apps-ui-kit': patch
+---
+
+Improve styling for small screens
```

### apps/ui-kit/src/lib/components/organisms/dialog/Dialog.tsx
```diff
@@ -68,17 +68,18 @@ const DialogContent = React.forwardRef<
         }, [containerId]);
         const positionClass =
             position === DialogPosition.Right
-                ? 'right-0 h-screen top-0 w-full'
-                : 'max-h-[60vh] left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-xl';
+                ? 'overflow-hidden right-0 h-screen top-0 w-full'
+                : 'overflow-y-auto overflow-x-hidden left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-xl';
         const widthClass =
             position === DialogPosition.Right ? 'md:w-96 max-w-[500px]' : customWidth;
+        const heightClass = position === DialogPosition.Right ? 'h-screen' : 'max-h-[80vh] h-full';
         return (
             <RadixDialog.Portal container={containerElement}>
                 <DialogOverlay showCloseIcon={showCloseOnOverlay} position={position} />
                 <RadixDialog.Content
                     ref={ref}
                     className={cx(
-                        'fixed z-[99999] flex flex-col justify-center overflow-hidden bg-primary-100 dark:bg-neutral-6',
+                        'fixed z-[99999] flex flex-col justify-center bg-primary-100 dark:bg-neutral-6',
                         positionClass,
                         widthClass,
                     )}
@@ -88,7 +89,7 @@ const DialogContent = React.forwardRef<
                         <RadixDialog.Title />
                         <RadixDialog.Description />
                     </VisuallyHidden.Root>
-                    {children}
+                    <div className={cx('flex flex-1 flex-col', heightClass)}>{children}</div>
                 </RadixDialog.Content>
             </RadixDialog.Portal>
         );
@@ -112,7 +113,7 @@ const DialogBody = React.forwardRef<React.ElementRef<'div'>, React.ComponentProp
     (props, ref) => (
         <div
             ref={ref}
-            className="p-md--rs text-body-sm text-neutral-40 dark:text-neutral-60"
+            className="flex-1 overflow-y-auto p-md--rs text-body-sm text-neutral-40 dark:text-neutral-60"
             {...props}
         />
     ),
```

### apps/wallet/src/ui/styles/global.scss
```diff
@@ -54,6 +54,7 @@ body {
     min-height: 100vh;
     background-size: cover;
     position: relative;
+    overflow-x: hidden;
     @apply bg-primary-90;
 }
 
```

### sdk/dapp-kit/src/components/connect-modal/views/ConnectionStatus.css.ts
```diff
@@ -12,6 +12,7 @@ export const container = style({
     justifyContent: 'center',
     alignItems: 'center',
     width: '100%',
+    overflowY: 'auto',
 });
 
 export const walletIcon = style({
```

### sdk/dapp-kit/src/components/connect-modal/views/GettingStarted.css.ts
```diff
@@ -8,6 +8,7 @@ export const container = style({
     display: 'flex',
     flexDirection: 'column',
     alignItems: 'center',
+    overflowY: 'auto',
 });
 
 export const content = style({
```

### sdk/dapp-kit/src/components/connect-modal/views/WhatIsAWallet.css.ts
```diff
@@ -17,4 +17,5 @@ export const content = style({
     flexGrow: 1,
     gap: 20,
     padding: 40,
+    overflowY: 'auto',
 });
```

### sdk/dapp-kit/src/components/connect-modal/wallet-list/WalletList.css.ts
```diff
@@ -9,6 +9,7 @@ export const container = style({
     display: 'flex',
     flexDirection: 'column',
     gap: 4,
+    overflowY: 'auto',
 });
 
 export const icon = style({
```
