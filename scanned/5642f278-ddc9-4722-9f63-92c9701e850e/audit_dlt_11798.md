# [?] fix(ramps): fixes quote race condition bug with missing payment method (#7863)

## Summary
Severity: Unknown
Chain: Tooling
Component: MetaMask/core
Published: 2026-02-09
Source: https://github.com/MetaMask/core/commit/a5e02ba7961e7742bf0586f817023f4d8a31fea3
Type: security-commit

## Details
fix(ramps): fixes quote race condition bug with missing payment method (#7863)

## Explanation

<!--
Thanks for your contribution! Take a moment to answer these questions so
that reviewers have the information they need to properly understand
your changes:

* What is the current state of things and why does it need to change?
* What is the solution your changes offer and how does it work?
* Are there any changes whose purpose might not obvious to those
unfamiliar with the domain?
* If your primary goal was to update one package but you found you had
to update another one along the way, why did you do so?
* If you had to upgrade a dependency, why did you do so?
-->

When switching the selected ramp token (e.g. ETH → BNB), the controller
clears the selected payment method and refetches payment methods for the
new token. The UI can still call startQuotePolling() in that window
(e.g. from a useEffect that hasn’t re-run with the updated state), so
the controller saw no payment method and threw.

FIX: 

In startQuotePolling(), if there is no selected payment method, return
early instead of throwing. Polling will start once payment methods are
loaded and the UI calls again. Region, token, and provider still throw
when missing, since they aren’t cleared then refetched on switch.

## References
<img width="427" height="933" alt="Screenshot 2026-02-07 at 3 08 03 PM"
src="https://github.com/user-attachments/assets/f5e857b9-b974-4d19-9749-3b65afb2a3db"
/>

<!--
Are there any issues that this pull request is tied to?
Are there other links that reviewers should consult to understand these
changes better?
Are there client or consumer pull requests to adopt any breaking
changes?

For example:

* Fixes #12345
* Related to #67890
-->

## Checklist

- [ ] I've updated the test suite for new or updated code as appropriate
- [ ] I've updated documentation (JSDoc, Markdown, etc.) for new or
updated code as appropriate
- [ ] I've communicated my changes to consumers by [updating changelogs
for packages I've
changed](https://github.com/MetaMask/core/tree/main/docs/processes/updating-changelogs.md)
- [ ] I've introduced [breaking
changes](https://github.com/MetaMask/core/tree/main/docs/processes/breaking-changes.md)
in this PR and have prepared draft pull requests for clients and
consumer packages to resolve them

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Small behavior change limited to quote polling startup error handling;
main risk is silently not starting polling if callers don’t retry once a
payment method is selected.
> 
> **Overview**
> Prevents a quote-polling race when switching tokens/providers by
changing `startQuotePolling()` to **return early** (instead of throwing)
if no payment method is currently selected.
> 
> Updates the associated unit test to assert non-throwing behavior, and
records the fix in the `ramps-controller` changelog under *Unreleased*.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
67672d9a1dcc04407dacf4bba5820c59eebb21ce. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### packages/ramps-controller/CHANGELOG.md
```diff
@@ -7,6 +7,10 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ## [Unreleased]
 
+### Fixed
+
+- Fixes quote race condition bug with missing payment method ([#7863](https://github.com/MetaMask/core/pull/7863))
+
 ## [7.0.0]
 
 ### Added
```

### packages/ramps-controller/src/RampsController.test.ts
```diff
@@ -4255,7 +4255,7 @@ describe('RampsController', () => {
       );
     });
 
-    it('throws error when payment method is not selected', async () => {
+    it('returns early without throwing when payment method is not selected', async () => {
       await withController(
         {
           options: {
@@ -4296,9 +4296,7 @@ describe('RampsController', () => {
               walletAddress: '0x1234567890abcdef1234567890abcdef12345678',
               amount: 100,
             }),
-          ).toThrow(
-            'Payment method is required. Cannot start quote polling without a selected payment method.',
-          );
+          ).not.toThrow();
         },
       );
     });
```

### packages/ramps-controller/src/RampsController.ts
```diff
@@ -1146,7 +1146,6 @@ export class RampsController extends BaseController<
     this.#fireAndForget(
       this.getPaymentMethods(regionCode, { assetId: token.assetId }).then(
         () => {
-          // Restart quote polling after payment methods are fetched
           this.#restartPollingIfActive();
           return undefined;
         },
@@ -1530,9 +1529,7 @@ export class RampsController extends BaseController<
     }
 
     if (!paymentMethod) {
-      throw new Error(
-        'Payment method is required. Cannot start quote polling without a selected payment method.',
-      );
+      return;
     }
 
     // Stop any existing polling first
```
