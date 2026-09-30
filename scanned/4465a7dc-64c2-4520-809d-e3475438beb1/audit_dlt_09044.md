# [?] fix: Prevent Snap crashing when clicking buttons without names cp-13.17.0 (#39727)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-02-03
Source: https://github.com/MetaMask/metamask-extension/commit/094fa7fdf6931ee7785e0bb7e67b38b9e6251509
Type: security-commit

## Details
fix: Prevent Snap crashing when clicking buttons without names cp-13.17.0 (#39727)

<!--
Please submit this PR as a draft initially.
Do not mark it as "Ready for review" until the template has been
completely filled out, and PR status checks have passed at least once.
-->

## **Description**

Fixes an issue introduced in
https://github.com/MetaMask/metamask-extension/commit/aa3b15527af237ab4fd7c1ba912398e19ee172f1
that caused Snaps to crash when using buttons without names. We changed
the fallback for `value` to `null` which gets passed as a parameter to
`onUserInput`. This is invalid and crashes the Snap.

[![Open in GitHub
Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MetaMask/metamask-extension/pull/39727?quickstart=1)

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

CHANGELOG entry: Prevent Snap crashing when clicking buttons without
names

## **Related issues**

https://consensyssoftware.atlassian.net/browse/WPC-362

## **Manual testing steps**

1. Install the following Snap:
https://snaps.metamask.io/snap/npm/quai-snap/
2. Go to its home page
3. Click send
4. Fill out the form with some bogus values (your own address and some
value)
5. Click send
6. Check that the Snap does not crash in the console

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Low risk, targeted change to Snap `onUserInput` event payloads; main
risk is subtle behavior change if any Snap relied on a `value` field for
`ButtonClickEvent`.
> 
> **Overview**
> Prevents Snaps from crashing when a submit `Button` has no `name` by
ensuring `ButtonClickEvent` requests never include a `value` field
(including `null`) in the `onUserInput` payload.
> 
> Adds a regression test covering form submission with an unnamed submit
button, asserting the emitted button-click event omits `name` and
`value` while form submission still includes the form `value` map.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
95c6fad5fea9551e2d796acc012f2840f8a7c393. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
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
