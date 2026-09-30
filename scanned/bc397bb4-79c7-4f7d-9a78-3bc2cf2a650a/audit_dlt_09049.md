# [?] fix: crash when clicking away from swap flow cp-13.10.0 (#37922)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2025-11-18
Source: https://github.com/MetaMask/metamask-extension/commit/85942073331814359e356c678da472c50220cc71
Type: security-commit

## Details
fix: crash when clicking away from swap flow cp-13.10.0 (#37922)

<!--
Please submit this PR as a draft initially.
Do not mark it as "Ready for review" until the template has been
completely filled out, and PR status checks have passed at least once.
-->

## **Description**

Adds additional typesafety in an assets selector used in the swap/bridge
experience to fix a crash.

<!--
Write a short description of the changes included in this pull request,
also include relevant motivation and context. Have in mind the following
questions:
1. What is the reason for the change?
2. What is the improvement/solution?
-->

[![Open in GitHub
Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MetaMask/metamask-extension/pull/37922?quickstart=1)

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

Fixes: https://github.com/MetaMask/metamask-extension/issues/37877

## **Manual testing steps**

1. Go to the swaps page on an imported account
2. Click away from the metamask popup
3. No crash should be observed

## **Screenshots/Recordings**

<!-- If applicable, add screenshots and/or recordings to visualize the
before and after of your change. -->

### **Before**

<!-- [screenshots/recordings] -->

### **After**

<!-- [screenshots/recordings] -->

## **Pre-merge author checklist**

- [x] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding
Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [x] I've completed the PR template to the best of my ability
- [x] I’ve included tests if applicable
- [x] I’ve documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [x] I’ve applied the right labels on the PR (see [labeling
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
> <sup>[Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) is
generating a summary for commit
e072afd8fa646494101512a6fdc2486755f27b9a. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### ui/selectors/assets.ts
```diff
@@ -558,6 +558,10 @@ export const getMultichainNativeTokenBalance = createDeepEqualSelector(
     multichainBalances: ReturnType<typeof getMultichainBalances>,
     nativeAssetType: ReturnType<typeof getMultichainNativeAssetType>,
   ) => {
+    if (!selectedAccountAddress) {
+      return zeroBalanceAssetFallback;
+    }
+
     const balances = multichainBalances?.[selectedAccountAddress.id];
 
     if (!nativeAssetType || !balances?.[nativeAssetType]) {
```
