# [?] fix: prevent tab index crash (#41658)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-04-13
Source: https://github.com/MetaMask/metamask-extension/commit/a296ea4c61ef8257d6fc3597406ffc851aa71ff1
Type: security-commit

## Details
fix: prevent tab index crash (#41658)

<!--
Please submit this PR as a draft initially.
Do not mark it as "Ready for review" until the template has been
completely filled out, and PR status checks have passed at least once.
-->

## **Description**

<!--
Write a short description of the changes included in this pull request,
also include relevant motivation and context. Have in mind the following
questions:
1. What is the reason for the change?
2. What is the improvement/solution?
-->

Prevent the tab component from crashing due to index out of bounds

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

Fixes: #41557

## **Manual testing steps**

1. Go to this page...
2.
3.

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
> **Low Risk**
> Low risk UI robustness change that prevents `Tabs` from throwing when
`activeTab` is missing or children change; behavior changes to fall back
to a valid tab instead of erroring.
> 
> **Overview**
> **Prevents `Tabs` from crashing on invalid/obsolete active tab
indices.** The active tab index is now clamped to the available children
and used consistently for `isActive`, click direction, and content
rendering, replacing the previous out-of-bounds throw.
> 
> Adds tests covering nonexistent `activeTab` keys and rerendering with
fewer children to ensure the component safely falls back to an existing
tab.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit
8db7b0658785778142d283f3e6969fd882146fb3. Bugbot is set up for automated
code reviews on this repo. Configure
[here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

### ui/components/ui/tabs/tabs.test.tsx
```diff
@@ -163,4 +163,47 @@ describe('Tabs', () => {
 
     expect(onTabClick).not.toHaveBeenCalled();
   });
+
+  it('clamps to last tab when activeTab key does not exist', () => {
+    const { getByText } = render(
+      <Tabs activeTab={'nonexistent' as string} onTabClick={() => null}>
+        <Tab tabKey="tab1" name="Tab 1">
+          Tab 1 Content
+        </Tab>
+        <Tab tabKey="tab2" name="Tab 2">
+          Tab 2 Content
+        </Tab>
+      </Tabs>,
+    );
+
+    expect(getByText('Tab 1 Content')).toBeInTheDocument();
+  });
+
+  it('does not crash when children are removed and activeTabIndex is out of bounds', () => {
+    const { rerender, getByText } = render(
+      <Tabs activeTab="tab3" onTabClick={() => null}>
+        <Tab tabKey="tab1" name="Tab 1">
+          Tab 1 Content
+        </Tab>
+        <Tab tabKey="tab2" name="Tab 2">
+          Tab 2 Content
+        </Tab>
+        <Tab tabKey="tab3" name="Tab 3">
+          Tab 3 Content
+        </Tab>
+      </Tabs>,
+    );
+
+    expect(getByText('Tab 3 Content')).toBeInTheDocument();
+
+    rerender(
+      <Tabs activeTab="tab3" onTabClick={() => null}>
+        <Tab tabKey="tab1" name="Tab 1">
+          Tab 1 Content
+        </Tab>
+      </Tabs>,
+    );
+
+    expect(getByText('Tab 1 Content')).toBeInTheDocument();
+  });
 });
```

### ui/components/ui/tabs/tabs.tsx
```diff
@@ -10,6 +10,10 @@ import { getBrowserName } from '../../../../shared/lib/browser-runtime.utils';
 import { PLATFORM_FIREFOX } from '../../../../shared/constants/app';
 import { TabsProps, TabChild } from './tabs.types';
 
+function clamp(value: number, min: number, max: number) {
+  return Math.max(min, Math.min(value, max));
+}
+
 async function startTransition(
   direction: 'forward' | 'backward',
   update: () => void,
@@ -78,9 +82,14 @@ export const Tabs = <TKey extends string = string>({
     }
   }, [activeTab, findChildByKey, activeTabIndex]);
 
+  const clampedIndex =
+    getValidChildren.length > 0
+      ? clamp(activeTabIndex, 0, getValidChildren.length - 1)
+      : 0;
+
   const handleTabClick = (tabIndex: number, tabKey: TKey): void => {
-    if (tabIndex !== activeTabIndex) {
-      const direction = tabIndex > activeTabIndex ? 'forward' : 'backward';
+    if (tabIndex !== clampedIndex) {
+      const direction = tabIndex > clampedIndex ? 'forward' : 'backward';
 
       const applyUpdate = () => {
         setActiveTabIndex(tabIndex);
@@ -106,7 +115,7 @@ export const Tabs = <TKey extends string = string>({
         ...child.props,
         onClick: (idx: number) => handleTabClick(idx, tabKey),
         tabIndex: index,
-        isActive: numberOfTabs > 1 && index === activeTabIndex,
+        isActive: numberOfTabs > 1 && index === clampedIndex,
         key: tabKey,
       });
     });
@@ -119,11 +128,7 @@ export const Tabs = <TKey extends string = string>({
       return null;
     }
 
-    if (activeTabIndex >= validChildren.length || activeTabIndex < 0) {
-      throw new Error(`Tab at index '${activeTabIndex}' does not exist`);
-    }
-
-    const activeChild = validChildren[activeTabIndex];
+    const activeChild = validChildren[clampedIndex];
     return activeChild?.props.children || null;
   };
 
```
