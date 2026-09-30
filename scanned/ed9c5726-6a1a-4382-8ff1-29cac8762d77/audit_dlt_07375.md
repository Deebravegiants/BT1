# [?] fix: rewards UI fixes button color and overflow (#37960)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2025-11-19
Source: https://github.com/MetaMask/metamask-extension/commit/14394287059e4d526e82450fe36e6658dbc63afc
Type: security-commit

## Details
fix: rewards UI fixes button color and overflow (#37960)

<!--
Please submit this PR as a draft initially.
Do not mark it as "Ready for review" until the template has been
completely filled out, and PR status checks have passed at least once.
-->

## **Description**
Duplicate of https://github.com/MetaMask/metamask-extension/pull/37818
rebased onto main
Small ui fixes to button color and prevent overflow
<!--
Write a short description of the changes included in this pull request,
also include relevant motivation and context. Have in mind the following
questions:
1. What is the reason for the change?
2. What is the improvement/solution?
-->

[![Open in GitHub
Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MetaMask/metamask-extension/pull/37960?quickstart=1)

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

- [x] I've manually tested the PR (e.g. pull and build branch, run the
app, test code being changed).
- [x] I confirm that this PR addresses all acceptance criteria described
in the ticket it closes and includes the necessary testing evidence such
as recordings and or screenshots.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Refines Rewards Onboarding modal layout and imagery to prevent
overflow, adjusts modal height, and adds button hover styling.
> 
> - **Rewards Onboarding UI**:
>   - **Layout/Sizing**:
>     - Reduce `OnboardingModal` height from `800px` to `740px`.
> - Tweak intro image positioning to `top: '25%'` and remove extra
margins.
> - Add `top: 0` to step SVGs; set step images to `width: '94%'` and
drop `w-full` to prevent overflow.
> - Adjust info containers (remove `min-h-30`, center content in Step 4)
for better vertical alignment.
>   - **Buttons**:
> - Add `hover:bg-default-hover` for the primary confirm button on the
intro step.
>     - Ensure skip button retains hover styling.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
2bc0e5fae48aabd9103ffd1e5148281ab2041c43. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### ui/components/app/rewards/onboarding/OnboardingIntroStep.tsx
```diff
@@ -191,8 +191,8 @@ const OnboardingIntroStep: React.FC = () => {
    */
   const renderImage = () => (
     <Box
-      className="flex justify-center items-center my-4 absolute"
-      style={{ top: 180 }}
+      className="flex justify-center items-center absolute"
+      style={{ top: '25%' }}
       data-testid="rewards-onboarding-intro-image"
     >
       <img
@@ -227,7 +227,7 @@ const OnboardingIntroStep: React.FC = () => {
           candidateSubscriptionId === 'retry'
         }
         onClick={handleNext}
-        className="w-full my-2 bg-white"
+        className="w-full my-2 bg-white hover:bg-default-hover"
       >
         <Text variant={TextVariant.BodyMd} className="text-black font-medium">
           {t('rewardsOnboardingIntroStepConfirm')}
```

### ui/components/app/rewards/onboarding/OnboardingModal.tsx
```diff
@@ -91,7 +91,7 @@ export default function OnboardingModal() {
           paddingTop: 0,
           paddingBottom: 0,
           style: {
-            height: '800px',
+            height: '740px',
             alignItems: 'center',
             justifyContent: 'center',
           },
```

### ui/components/app/rewards/onboarding/OnboardingStep1.tsx
```diff
@@ -31,7 +31,7 @@ const OnboardingStep1: React.FC = () => {
         xmlns="http://www.w3.org/2000/svg"
         aria-hidden="true"
         focusable="false"
-        style={{ left: 0 }}
+        style={{ left: 0, top: 0 }}
       >
         <path
           d="M 302.98438 0 L 213.17773 113.25586 L 162.85742 113.25586 L 162.85742 224.83594 L 162.84766 224.83594 L 162.84766 113.09766 L 62.902344 113.09766 L -37.042969 226.49805 L -37.042969 339.89844 L 62.902344 339.89844 L 162.8125 226.53711 L 162.8125 339.9707 L 212.77539 339.9707 L 212.77539 340.4043 L 302.69336 453.79883 L 392.61523 453.79883 L 392.61523 340.4043 L 361.58008 301.26758 L 361.58008 224.83594 L 304.5332 224.83594 L 392.90625 113.39453 L 392.90625 0 L 302.98438 0 z "
@@ -41,15 +41,16 @@ const OnboardingStep1: React.FC = () => {
 
       <img
         src="https://images.ctfassets.net/9sy2a0egs6zh/5ieKFEvd1qM3crY76W751i/ab846811e550d4a84c12a063f468f30c/rewards-onboarding-step1.png"
-        className="w-full z-10 object-contain"
+        className="z-10 object-contain"
         data-testid="rewards-onboarding-step1-image"
+        width={'94%'}
       />
     </>
   );
 
   const renderStepInfo = () => (
     <Box
-      className="flex flex-col min-h-30 gap-2 flex-1 justify-end"
+      className="flex flex-col gap-2 flex-1 justify-end"
       data-testid="rewards-onboarding-step1-info"
     >
       <Text variant={TextVariant.HeadingLg} className="text-center">
```

### ui/components/app/rewards/onboarding/OnboardingStep2.tsx
```diff
@@ -31,7 +31,7 @@ const OnboardingStep2: React.FC = () => {
         xmlns="http://www.w3.org/2000/svg"
         aria-hidden="true"
         focusable="false"
-        style={{ left: 0 }}
+        style={{ left: 0, top: 0 }}
       >
         <path
           d="M 257.61523 0 L 121.50195 136.11328 L 121.50195 272.51562 L 30.742188 272.51562 L 30.742188 363.25781 L 166.87109 363.25781 L 166.87109 454 L 302.98438 454 L 393.72852 363.25781 L 393.71289 363.25781 L 393.71289 272.51562 L 393.73047 272.51562 L 302.79492 227.04688 L 393.73047 136.11328 L 393.73047 0 L 257.61523 0 z M 30.742188 363.25781 L -60 363.25781 L -60 454 L 30.742188 454 L 30.742188 363.25781 z M -59.998047 45.660156 L -14.626953 136.40234 L 121.48633 136.40234 L 76.115234 45.660156 L -59.998047 45.660156 z M 121.48633 181.76953 L 30.744141 272.51367 L 121.48633 272.51367 L 121.48633 181.76953 z M 212.24414 272.36914 L 212.24414 272.51562 L 165.20898 272.51562 L 212.24414 272.36914 z "
@@ -41,15 +41,16 @@ const OnboardingStep2: React.FC = () => {
 
       <img
         src="https://images.ctfassets.net/9sy2a0egs6zh/2wG5gvQmC4d95TShVVpsEX/9bd7f199f47833fdc68e403a059713df/rewards-onboarding-step2.png"
-        className="w-full z-10 object-contain"
+        className="z-10 object-contain"
         data-testid="rewards-onboarding-step2-image"
+        width={'94%'}
       />
     </>
   );
 
   const renderStepInfo = () => (
     <Box
-      className="flex flex-col min-h-30 gap-2 flex-1 justify-end"
+      className="flex flex-col gap-2 flex-1 justify-end"
       data-testid="rewards-onboarding-step2-info"
     >
       <Text variant={TextVariant.HeadingLg} className="text-center">
```

### ui/components/app/rewards/onboarding/OnboardingStep3.tsx
```diff
@@ -31,7 +31,7 @@ const OnboardingStep3: React.FC = () => {
         xmlns="http://www.w3.org/2000/svg"
         aria-hidden="true"
         focusable="false"
-        style={{ left: 0 }}
+        style={{ left: 0, top: 0 }}
       >
         <path
           d="M 294.88086 0 L 197.81836 90.767578 L 197.81836 181.53516 L 294.88086 181.53516 L 294.93555 181.48438 L 294.93555 181.54102 L 197.94922 181.54102 L 197.94922 272 L 99 272 L 0 362.99805 L 0 454 L 99 454 L 198 362.99805 L 198 362.81641 L 294.84375 272.27148 L 294.93555 272.27148 L 294.93555 362.11914 L 392 362.11914 L 392 181.35938 L 295.06836 181.35938 L 391.94336 90.767578 L 391.94336 0 L 294.88086 0 z "
@@ -41,15 +41,16 @@ const OnboardingStep3: React.FC = () => {
 
       <img
         src="https://images.ctfassets.net/9sy2a0egs6zh/7ERFcIMMLMTL4EekVoOana/a03bef86b2cb4f87fc5ee84afd427d21/rewards-onboarding-step3.png"
-        className="w-full z-10 object-contain"
+        className="z-10 object-contain"
         data-testid="rewards-onboarding-step3-image"
+        width={'94%'}
       />
     </>
   );
 
   const renderStepInfo = () => (
     <Box
-      className="flex flex-col min-h-30 gap-2 flex-1 justify-end"
+      className="flex flex-col gap-2 flex-1 justify-end"
       data-testid="rewards-onboarding-step3-info"
     >
       <Text variant={TextVariant.HeadingLg} className="text-center">
```

### ui/components/app/rewards/onboarding/OnboardingStep4.tsx
```diff
@@ -96,16 +96,17 @@ const OnboardingStep4: React.FC = () => {
 
   const renderStepInfo = () => (
     <Box
-      className="flex flex-col min-h-30 gap-4 flex-1 justify-end"
+      className="flex flex-col flex-1 gap-4 justify-center"
       data-testid="rewards-onboarding-step4-info"
     >
       <img
         src="https://images.ctfassets.net/9sy2a0egs6zh/2W921m9iDZsozDlv1pNx4z/c04e3577afd665ae5434d8b7115c4bcc/rewards-onboarding-step4.png"
-        className="z-10 object-contain self-center my-4"
+        className="z-10 object-contain self-center"
         width={100}
         height={100}
         alt={t('rewardsOnboardingStep4Title')}
       />
+
       <Text variant={TextVariant.HeadingLg} className="text-center">
         {referralCodeIsValid
           ? t('rewardsOnboardingStep4TitleWithReferralCode')
```
