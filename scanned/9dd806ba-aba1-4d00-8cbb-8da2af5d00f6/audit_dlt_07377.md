# [?] release(runway): cherry-pick fix: menu height overflow cp-13.10.0 (#37947)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2025-11-18
Source: https://github.com/MetaMask/metamask-extension/commit/01799a39acaa15c97acd13ca27427a0facab7e68
Type: security-commit

## Details
release(runway): cherry-pick fix: menu height overflow cp-13.10.0 (#37947)

- fix: menu height overflow cp-13.10.0 (#37915)

## **Description**

Allow the main menu to scroll when height > viewport height

Without this, the user can't navigate to the item down the list because
scrolling will hide it

[![Open in GitHub

Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MetaMask/metamask-extension/pull/37915?quickstart=1)

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

CHANGELOG entry: fix: menu height overflow

## **Related issues**

Fixes: https://consensyssoftware.atlassian.net/browse/CEUX-710

## **Manual testing steps**

1. Shorten the window height
2. Open sidepanel or full view

## **Screenshots/Recordings**

<!-- If applicable, add screenshots and/or recordings to visualize the
before and after of your change. -->

### **Before**

<!-- [screenshots/recordings] -->

### **After**

<img width="238" height="439" alt="image"

src="https://github.com/user-attachments/assets/0abbad1d-8b8a-49cc-8852-87b7d2d74ceb"
/>


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
> Makes the global menu scrollable within the viewport and replaces
hardcoded header heights with the --header-height CSS variable.
> 
> - **UI**
> - **Global menu
(`ui/components/multichain/global-menu/global-menu.tsx`)**:
> - Constrains popover with `maxHeight: calc(100vh -
var(--header-height))` and enables scrolling via `overflow-y-auto`.
>   - **App header (`ui/components/multichain/app-header/index.scss`)**:
>     - Replaces hardcoded `68px` heights with `var(--header-height)`.
>   - **Base styles (`ui/css/base-styles.scss`)**:
>     - Defines `--header-height: 68px` CSS variable.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
68cac866e0879e5341f4db3ffdb811a5fc6e4952. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->


[7631e92](https://github.com/MetaMask/metamask-extension/commit/7631e92524e9ad5d7188becd814856f1bea97706)

Co-authored-by: Francis Nepomuceno <n3ps@users.noreply.github.com>

## Patch
### ui/components/multichain/app-header/index.scss
```diff
@@ -10,10 +10,10 @@
   max-width: 100%;
   flex-flow: column nowrap;
   z-index: design-system.$header-z-index;
-  min-height: 68px;
+  min-height: var(--header-height);
 
   &__contents {
-    height: 68px;
+    height: var(--header-height);
 
     &__network-picker {
       max-width: 250px;
@@ -36,7 +36,7 @@
 
   &__lock-contents {
     flex-flow: row nowrap;
-    height: 68px;
+    height: var(--header-height);
 
     @include design-system.screen-sm-max {
       height: $height-screen-sm-max;
```

### ui/components/multichain/global-menu/global-menu.tsx
```diff
@@ -352,11 +352,12 @@ export const GlobalMenu = ({
       onClickOutside={closeMenu}
       onPressEscKey={closeMenu}
       style={{
-        overflow: 'hidden',
         minWidth: 225,
+        maxHeight: 'calc(100vh - var(--header-height))',
       }}
       offset={[0, 8]}
       position={PopoverPosition.BottomEnd}
+      className="overflow-y-auto"
     >
       {basicFunctionality && (
         <>
```

### ui/css/base-styles.scss
```diff
@@ -8,6 +8,7 @@
   --width-sm: 576px;
   --width-max: 798px;
   --width-max-sidepanel: 490px;
+  --header-height: 68px;
 }
 
 html,
```
