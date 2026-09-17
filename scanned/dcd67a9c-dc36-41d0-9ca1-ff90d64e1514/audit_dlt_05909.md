# [?] fix: crash when typing a comma in the MM Pay custom amount input (#44521)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-07-16
Source: https://github.com/MetaMask/metamask-extension/commit/449919f4848d693a0f1c48eae9fee842d04e9764
Type: security-commit

## Details
fix: crash when typing a comma in the MM Pay custom amount input (#44521)

## **Description**

Typing a comma as the decimal separator in the MM Pay custom amount
input (Perps withdraw/deposit, mUSD conversion) crashed the extension UI
with `BigNumber Error: new BigNumber() not a number: 0,`.

The input field intentionally accepts a comma
(`/^[0-9]*[.,]?[0-9]*$/u`), but `updatePendingAmount` stored the value
without normalizing it. The comma value then reached `new
BigNumber(amountFiat)` during render, which throws, so the confirmation
crashed to the error screen on the first comma keypress.

The fix normalizes the comma to a dot inside `updatePendingAmount`, the
single point all amount input goes through before reaching state. This
matches how `snap-ui-input.tsx` and the legacy Perps withdraw page
already handle commas. Since the input regex allows at most one
separator, a single `replace(',', '.')` is enough.

## **Changelog**

CHANGELOG entry: Fixed a crash when typing a comma as the decimal
separator in the amount field of MetaMask Pay confirmations, such as
Perps withdraw or mUSD conversion

## **Related issues**

Fixes: CONF-1696

## **Manual testing steps**

1. Open an MM Pay custom amount confirmation, e.g. Perps withdraw (with
the withdraw-to-any-token flag enabled) or Perps deposit
2. Type an amount using a comma as the decimal separator, e.g. `0,5`
3. Verify the input shows `0.5`, the extension does not crash, and
quotes load for the amount
4. Verify typing with a dot (`0.5`) still works as before

## **Screenshots/Recordings**

### **Before**

_visual proof in progress_

### **After**

_visual proof in progress_

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

### ui/pages/confirmations/hooks/transactions/useTransactionCustomAmount.test.ts
```diff
@@ -195,6 +195,38 @@ describe('useTransactionCustomAmount', () => {
       expect(result.current.amountFiat).toBe('0.5');
     });
 
+    it('normalizes a comma decimal separator to a dot', () => {
+      const { result } = runHook();
+
+      act(() => {
+        result.current.updatePendingAmount('1,5');
+      });
+
+      expect(result.current.amountFiat).toBe('1.5');
+      expect(result.current.amountHuman).toBe('1.5');
+    });
+
+    it('adds leading zero for inputs starting with comma', () => {
+      const { result } = runHook();
+
+      act(() => {
+        result.current.updatePendingAmount(',5');
+      });
+
+      expect(result.current.amountFiat).toBe('0.5');
+    });
+
+    it('keeps the amount parseable when input ends with a comma', () => {
+      const { result } = runHook();
+
+      act(() => {
+        result.current.updatePendingAmount('0,');
+      });
+
+      expect(result.current.amountFiat).toBe('0.');
+      expect(result.current.amountHuman).toBe('0');
+    });
+
     it('ignores input exceeding MAX_LENGTH', () => {
       const { result } = runHook();
 
```

### ui/pages/confirmations/hooks/transactions/useTransactionCustomAmount.ts
```diff
@@ -162,9 +162,11 @@ export function useTransactionCustomAmount({
       // before the debounced `isInputChanged` catches up.
       userEditedRef.current = true;
 
-      let newAmount = value.replace(/^0+/u, '') || '0';
+      // The input allows a comma as decimal separator, but BigNumber throws
+      // on commas, so normalize it to a dot before it reaches state.
+      let newAmount = value.replace(',', '.').replace(/^0+/u, '') || '0';
 
-      if (newAmount.startsWith('.') || newAmount.startsWith(',')) {
+      if (newAmount.startsWith('.')) {
         newAmount = `0${newAmount}`;
       }
 
```
