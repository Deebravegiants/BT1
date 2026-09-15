# [?] fix: update race condition for browser to set the state (#45571)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-08-17
Source: https://github.com/MetaMask/metamask-extension/commit/ef798ef7d8e572e76a5a122eea530e3b902e8773
Type: security-commit

## Details
fix: update race condition for browser to set the state (#45571)

This PR fixed an issue where MetaMask could reopen as a popup after
switching to Sidepanel

## **Description**

<!--
Write a short description of the changes included in this pull request,
also include relevant motivation and context. Have in mind the following
questions:
1. What is the reason for the change?
2. What is the improvement/solution?
-->

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

CHANGELOG entry: null

## **Related issues**

Fixes:

## **Manual testing steps**

1. Open MetaMask as a popup and use the global menu to switch to
Sidepanel.
2. Verify the popup closes and the Sidepanel opens.
3. Click the MetaMask toolbar icon several times; verify it
opens/toggles the Sidepanel rather than opening a popup.
4. Close and reopen Chrome, then click the MetaMask toolbar icon; verify
it opens the Sidepanel.
5. In Sidepanel, use the global menu to switch back to Popup.
6. Click the MetaMask toolbar icon and verify it opens the popup.

## **Screenshots/Recordings**

<!-- If applicable, add screenshots and/or recordings to visualize the
before and after of your change. -->

### **Before**

<!-- [screenshots/recordings] -->

### **After**

<!-- [screenshots/recordings] -->

## **Pre-merge author checklist**

- [ ] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding
Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [ ] I've completed the PR template to the best of my ability
- [ ] I’ve included tests if applicable
- [ ] I’ve documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [ ] I’ve applied the right labels on the PR (see [labeling
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
> <sup>[Cursor Bugbot](https://cursor.com/bugbot) is generating a
summary for commit 5f517eeffaf38017a8e723e936215a38ace96938. Configure
[here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

### ui/store/actions.toggle-default-view.test.ts
```diff
@@ -161,10 +161,6 @@ describe('toggleDefaultView', () => {
       await store.dispatch(toggleDefaultView() as never);
 
       expect(browserMock.sidePanel.open).toHaveBeenCalledWith({ windowId: 1 });
-      expect(setPreferenceCalls(setPreferenceBackground)).not.toContainEqual([
-        'useSidePanelAsDefault',
-        true,
-      ]);
       expect(closeSpy).not.toHaveBeenCalled();
     });
 
```

### ui/store/actions.ts
```diff
@@ -4352,6 +4352,8 @@ export function toggleDefaultView(): ThunkAction<
         // closing the popup, and skip persisting the preference, leaving both
         // surfaces open and the next launch defaulting back to the popup.
         try {
+          // Persist the preference
+          await dispatch(setUseSidePanelAsDefault(true));
           await browserWithSidePanel.sidePanel.open({ windowId });
         } catch (error) {
           // Nothing was opened, so the popup stays and state is consistent.
@@ -4361,11 +4363,6 @@ export function toggleDefaultView(): ThunkAction<
           );
           return;
         }
-
-        // Persist the preference before closing the popup so a reopen always
-        // honors the side panel choice and the background toolbar-behavior
-        // subscription flips to open-on-click.
-        await dispatch(setUseSidePanelAsDefault(true));
         window.close();
       }
     } catch (error) {
```
