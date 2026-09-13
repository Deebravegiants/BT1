# [?] fix: content overflow on transaction shield pages (#41990)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-04-21
Source: https://github.com/MetaMask/metamask-extension/commit/176b0552658c502869c6cb8219684eec14924e50
Type: security-commit

## Details
fix: content overflow on transaction shield pages (#41990)

<!--
Please submit this PR as a draft initially.
Do not mark it as "Ready for review" until the template has been
completely filled out, and PR status checks have passed at least once.
-->

## **Description**
This fixes contents overflowing on Settings > Transaction Shield/Claims
pages

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

CHANGELOG entry: Fix content overflow on Transaction shield pages

## **Related issues**

Fixes:

## **Manual testing steps**

1. Login with an account with shield subcscription
2. Go to Menu > Settings > Transaction Shield
3. Make browser height smaller until scroll bar shows up (try scrolling
down)
4. Go to Menu > Settings > Transaction Shield > Claims > Submit a claim
5. Try scrolling down

## **Screenshots/Recordings**

<!-- If applicable, add screenshots and/or recordings to visualize the
before and after of your change. -->

### **Before**

https://github.com/user-attachments/assets/f88b6df6-a903-4f04-8029-77675cec0272

<!-- [screenshots/recordings] -->

### **After**

https://github.com/user-attachments/assets/a91c6efb-00ba-4543-a9c0-bbc25176b166

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
> UI-only className changes to scrolling/padding with no changes to
business logic, data handling, or API behavior.
> 
> **Overview**
> Prevents content overflow on Transaction Shield settings screens by
making the main page containers vertically scrollable.
> 
> Adds `overflow-y-auto` (and bottom padding) to the root `Box` wrappers
in `transaction-shield.tsx`, `manage-shield-plan.tsx` (including its
error state), and the Claims `claims-form.tsx` submit page so long
content can be scrolled instead of clipping.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit
1382db8f79675f997f4c7b208a2f2ec7368ee29c. Bugbot is set up for automated
code reviews on this repo. Configure
[here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

### ui/pages/settings/transaction-shield-tab/claims-form/claims-form.tsx
```diff
@@ -559,7 +559,7 @@ const ClaimsForm = ({
 
   return (
     <Box
-      className="submit-claim-page flex flex-col pt-4 px-4 pb-4"
+      className="submit-claim-page flex flex-col pt-4 px-4 pb-4 overflow-y-auto"
       data-testid="submit-claim-page"
       gap={4}
     >
```

### ui/pages/settings/transaction-shield-tab/manage-shield-plan/manage-shield-plan.tsx
```diff
@@ -166,7 +166,7 @@ const ManageShieldPlan = ({ isPastPlan = false }: { isPastPlan?: boolean }) => {
   if (!loading && hasApiError) {
     return (
       <Box
-        className="transaction-shield-page w-full"
+        className="transaction-shield-page w-full pb-4 overflow-y-auto"
         data-testid="transaction-shield-page"
         padding={4}
       >
@@ -181,7 +181,7 @@ const ManageShieldPlan = ({ isPastPlan = false }: { isPastPlan?: boolean }) => {
 
   return (
     <Box
-      className="manage-plan-page w-full h-full flex flex-col"
+      className="manage-plan-page w-full h-full flex flex-col pb-4 overflow-y-auto"
       data-testid="manage-plan-page"
     >
       <MembershipErrorBanner
```

### ui/pages/settings/transaction-shield-tab/transaction-shield.tsx
```diff
@@ -431,7 +431,7 @@ const TransactionShield = () => {
   if (!loading && hasApiError) {
     return (
       <Box
-        className="transaction-shield-page w-full"
+        className="transaction-shield-page w-full pb-4 overflow-y-auto"
         data-testid="transaction-shield-page"
       >
         <ApiErrorHandler
@@ -446,7 +446,7 @@ const TransactionShield = () => {
 
   return (
     <Box
-      className="transaction-shield-page flex flex-col w-full"
+      className="transaction-shield-page flex flex-col w-full pb-4 overflow-y-auto"
       data-testid="transaction-shield-page"
     >
       {currentShieldSubscription?.cancelAtPeriodEnd && (
```
