# [?] fix: fixes recipient modal long text overflow (#38454)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2025-12-02
Source: https://github.com/MetaMask/metamask-extension/commit/b2dc4a2da714b1bf6a6682636885a4cca9be97b4
Type: security-commit

## Details
fix: fixes recipient modal long text overflow (#38454)

## **Description**

The destination account picker modal was experiencing horizontal
overflow when account names were long (e.g., external addresses used as
names). This created a poor UX with horizontal scrolling.

The fix adds proper overflow handling to the account name container:
- Added `overflow: hidden`, `flex: 1`, and `minWidth: 0` to the Column
containing the name (the `minWidth: 0` is key for flex children to allow
shrinking below content size)
- Added `overflow: hidden` to the Row
- Added explicit `textOverflow: ellipsis` to the Text component
- Added `flexShrink: 0` to the checkmark icon so it doesn't get squished

Now long account names are properly truncated with an ellipsis instead
of causing overflow.

[![Open in GitHub
Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MetaMask/metamask-extension/pull/38454?quickstart=1)

## **Changelog**

CHANGELOG entry: Fixed recipient modal overflow when account names are
long

## **Related issues**

Fixes: https://github.com/MetaMask/metamask-extension/issues/38107

## **Manual testing steps**

1. Create or import an account with a very long name (or use an external
address as an account name)
2. Go to the Bridge page
3. Select a non-EVM chain (Bitcoin or Solana) as the destination
4. Open the destination account picker modal
5. Verify that long account names are truncated with an ellipsis instead
of causing horizontal overflow
6. Verify the modal layout looks clean without horizontal scrolling

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
> Prevents horizontal overflow in the destination account picker by
constraining flex children and adding ellipsis truncation; updates
snapshots accordingly.
> 
> - **UI (Destination account picker)**:
> - In
`ui/pages/bridge/prepare/components/destination-account-list-item.tsx`:
> - Add `style={{ overflow: 'hidden', flex: 1, minWidth: 0 }}` to
`Column` wrapping the name.
> - Set `Row` to `style={{ overflow: 'hidden' }}` and `Text` to
`style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}` with
`ellipsis` prop.
> - Prevent check icon from shrinking via `style={{ flexShrink: 0 }}`.
> - **Tests**:
> - Update snapshots in
`__snapshots__/destination-account-picker-modal.test.tsx.snap` to
reflect new overflow, flex, and ellipsis styles.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
17f58cde5124d1b52d279f1694dd9c7f02e0c2ab. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### ui/pages/bridge/prepare/components/__snapshots__/destination-account-picker-modal.test.tsx.snap
```diff
@@ -135,19 +135,22 @@ exports[`DestinationAccountPickerModal should render the modal when an account i
             <div
               class="mm-box mm-container mm-container--max-width-undefined mm-box--display-flex mm-box--gap-1 mm-box--flex-direction-column mm-box--width-full"
               data-testid="selected-to-account"
+              style="overflow: hidden; flex: 1; min-width: 0;"
             >
               <div
                 class="mm-box mm-container mm-container--max-width-undefined mm-box--display-flex mm-box--gap-1 mm-box--flex-direction-row mm-box--flex-wrap-nowrap mm-box--justify-content-space-between mm-box--align-items-center"
-                style="max-width: min-content;"
+                style="overflow: hidden;"
               >
                 <p
                   class="mm-box mm-text mm-text--body-md-medium mm-text--ellipsis mm-box--color-text-default"
+                  style="overflow: hidden; text-overflow: ellipsis;"
                 >
                   Ledger Account 1
                 </p>
                 <svg
                   class="inline-block w-5 h-5 text-primary-default"
                   fill="currentColor"
+                  style="flex-shrink: 0;"
                   viewBox="0 0 24 24"
                   xmlns="http://www.w3.org/2000/svg"
                 >
@@ -243,13 +246,15 @@ exports[`DestinationAccountPickerModal should render the modal when an account i
             </div>
             <div
               class="mm-box mm-container mm-container--max-width-undefined mm-box--display-flex mm-box--gap-1 mm-box--flex-direction-column mm-box--width-full"
+              style="overflow: hidden; flex: 1; min-width: 0;"
             >
               <div
                 class="mm-box mm-container mm-container--max-width-undefined mm-box--display-flex mm-box--gap-1 mm-box--flex-direction-row mm-box--flex-wrap-nowrap mm-box--justify-content-space-between mm-box--align-items-center"
-                style="max-width: min-content;"
+                style="overflow: hidden;"
               >
                 <p
                   class="mm-box mm-text mm-text--body-md-medium mm-text--ellipsis mm-box--color-text-default"
+                  style="overflow: hidden; text-overflow: ellipsis;"
                 >
                   Account 1
                 </p>
@@ -341,13 +346,15 @@ exports[`DestinationAccountPickerModal should render the modal when an account i
             </div>
             <div
               class="mm-box mm-container mm-container--max-width-undefined mm-box--display-flex mm-box--gap-1 mm-box--flex-direction-column mm-box--width-full"
+              style="overflow: hidden; flex: 1; min-width: 0;"
             >
               <div
                 class="mm-box mm-container mm-container--max-width-undefined mm-box--display-flex mm-box--gap-1 mm-box--flex-direction-row mm-box--flex-wrap-nowrap mm-box--justify-content-space-between mm-box--align-items-center"
-                style="max-width: min-content;"
+                style="overflow: hidden;"
               >
                 <p
                   class="mm-box mm-text mm-text--body-md-medium mm-text--ellipsis mm-box--color-text-default"
+                  style="overflow: hidden; text-overflow: ellipsis;"
                 >
                   Account 2
                 </p>
@@ -531,13 +538,15 @@ exports[`DestinationAccountPickerModal should render the modal when no account i
             </div>
             <div
               class="mm-box mm-container mm-container--max-width-undefined mm-box--display-flex mm-box--gap-1 mm-box--flex-direction-column mm-box--width-full"
+              style="overflow: hidden; flex: 1; min-width: 0;"
             >
               <div
                 class="mm-box mm-container mm-container--max-width-undefined mm-box--display-flex mm-box--gap-1 mm-box--flex-direction-row mm-box--flex-wrap-nowrap mm-box--justify-content-space-between mm-box--align-items-center"
-                style="max-width: min-content;"
+                style="overflow: hidden;"
               >
                 <p
                   class="mm-box mm-text mm-text--body-md-medium mm-text--ellipsis mm-box--color-text-default"
+                  style="overflow: hidden; text-overflow: ellipsis;"
                 >
                   Ledger Account 1
                 </p>
@@ -629,13 +638,15 @@ exports[`DestinationAccountPickerModal should render the modal when no account i
             </div>
             <div
               class="mm-box mm-container mm-container--max-width-undefined mm-box--display-flex mm-box--gap-1 mm-box--flex-direction-column mm-box--width-full"
+              style="overflow: hidden; flex: 1; min-width: 0;"
             >
               <div
                 class="mm-box mm-container mm-container--max-width-undefined mm-box--display-flex mm-box--gap-1 mm-box--flex-direction-row mm-box--flex-wrap-nowrap mm-box--justify-content-space-between mm-box--align-items-center"
-                style="max-width: min-content;"
+                style="overflow: hidden;"
               >
                 <p
                   class="mm-box mm-text mm-text--body-md-medium mm-text--ellipsis mm-box--color-text-default"
+                  style="overflow: hidden; text-overflow: ellipsis;"
                 >
                   Account 1
                 </p>
@@ -727,13 +738,15 @@ exports[`DestinationAccountPickerModal should render the modal when no account i
             </div>
             <div
               class="mm-box mm-container mm-container--max-width-undefined mm-box--display-flex mm-box--gap-1 mm-box--flex-direction-column mm-box--width-full"
+              style="overflow: hidden; flex: 1; min-width: 0;"
             >
               <div
                 class="mm-box mm-container mm-container--max-width-undefined mm-box--display-flex mm-box--gap-1 mm-box--flex-direction-row mm-box--flex-wrap-nowrap mm-box--justify-content-space-between mm-box--align-items-center"
-                style="max-width: min-content;"
+                style="overflow: hidden;"
               >
                 <p
                   class="mm-box mm-text mm-text--body-md-medium mm-text--ellipsis mm-box--color-text-default"
+                  style="overflow: hidden; text-overflow: ellipsis;"
                 >
                   Account 2
                 </p>
```

### ui/pages/bridge/prepare/components/destination-account-list-item.tsx
```diff
@@ -135,16 +135,22 @@ const DestinationAccountListItem: React.FC<DestinationAccountListItemProps> = ({
       <Column
         gap={1}
         data-testid={selected ? 'selected-to-account' : undefined}
+        style={{ overflow: 'hidden', flex: 1, minWidth: 0 }}
       >
-        <Row gap={1} style={{ maxWidth: 'min-content' }}>
-          <Text variant={TextVariant.bodyMdMedium} ellipsis>
+        <Row gap={1} style={{ overflow: 'hidden' }}>
+          <Text
+            variant={TextVariant.bodyMdMedium}
+            ellipsis
+            style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}
+          >
             {account.displayName}
           </Text>
           {selected && (
             <Icon
               name={IconName.CheckBold}
               size={IconSize.Md}
               color={IconColor.PrimaryDefault}
+              style={{ flexShrink: 0 }}
             />
           )}
         </Row>
```
