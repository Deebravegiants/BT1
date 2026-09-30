# [?] release(runway): cherry-pick fix: Prevent Snap crashing when clicking buttons without names cp-13.17.0 (#39732)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-02-03
Source: https://github.com/MetaMask/metamask-extension/commit/6a1026c4a62918249963125a28c1c9b9b5b4c9a5
Type: security-commit

## Details
release(runway): cherry-pick fix: Prevent Snap crashing when clicking buttons without names cp-13.17.0 (#39732)

- fix: Prevent Snap crashing when clicking buttons without names cp-13.17.0 (#39727)

CHANGELOG entry: Prevented Snap crashing when clicking buttons without names

## Patch
### CHANGELOG.md
```diff
@@ -56,6 +56,7 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 - Fixed critical performance issue slowing down all user actions by fixing confirmations selector memoization (#39313)
 - Fixed an issue where cancelling a Shield subscription payment on Stripe's checkout page was incorrectly treated as an error (#39513)
 - Purge profile service on resetting wallet (#39665)
+- Prevented Snap crashing when clicking buttons without names (#39727)
 
 ## [13.16.0]
 
```

### ui/components/app/snaps/snap-ui-renderer/components/form.test.ts
```diff
@@ -251,4 +251,78 @@ describe('SnapUIForm', () => {
 
     expect(container).toMatchSnapshot();
   });
+
+  it('submits correctly when button has no name', () => {
+    const { getByRole } = renderInterface(
+      Box({
+        children: Form({
+          name: 'form',
+          children: [
+            Field({ label: 'My Input', children: Input({ name: 'input' }) }),
+            Field({
+              label: 'Checkbox',
+              children: Checkbox({ name: 'checkbox' }),
+            }),
+            Button({ type: 'submit', children: 'Submit' }),
+          ],
+        }),
+      }),
+    );
+
+    const input = getByRole('textbox');
+    fireEvent.change(input, { target: { value: 'abc' } });
+
+    const checkbox = getByRole('checkbox');
+    fireEvent.click(checkbox);
+
+    const button = getByRole('button');
+    fireEvent.click(button);
+
+    expect(submitRequestToBackground).toHaveBeenNthCalledWith(
+      5,
+      'handleSnapRequest',
+      [
+        {
+          handler: 'onUserInput',
+          origin: 'metamask',
+          request: {
+            jsonrpc: '2.0',
+            method: ' ',
+            params: {
+              event: { type: 'ButtonClickEvent' },
+              id: MOCK_INTERFACE_ID,
+            },
+          },
+          snapId: MOCK_SNAP_ID,
+        },
+      ],
+    );
+
+    expect(submitRequestToBackground).toHaveBeenNthCalledWith(
+      6,
+      'handleSnapRequest',
+      [
+        {
+          handler: 'onUserInput',
+          origin: 'metamask',
+          request: {
+            jsonrpc: '2.0',
+            method: ' ',
+            params: {
+              event: {
+                name: 'form',
+                type: 'FormSubmitEvent',
+                value: {
+                  checkbox: true,
+                  input: 'abc',
+                },
+              },
+              id: MOCK_INTERFACE_ID,
+            },
+          },
+          snapId: MOCK_SNAP_ID,
+        },
+      ],
+    );
+  });
 });
```

### ui/contexts/snaps/snap-interface.tsx
```diff
@@ -105,7 +105,11 @@ export const SnapInterfaceContextProvider: FunctionComponent<
           event: {
             type: event,
             ...(name === undefined ? {} : { name }),
-            ...(value === undefined ? {} : { value }),
+            // Ensure `value` is always stripped for button clicks as buttons do not have a value (null is also disallowed).
+            ...(event === UserInputEventType.ButtonClickEvent ||
+            value === undefined
+              ? {}
+              : { value }),
           },
           id: interfaceId,
         },
```
