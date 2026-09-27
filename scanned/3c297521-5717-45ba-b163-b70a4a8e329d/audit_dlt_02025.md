# [?] release(runway): cherry-pick fix:  musd conversion flow selected payToken race condition (#41800)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-04-16
Source: https://github.com/MetaMask/metamask-extension/commit/2fc2d8ba07773a78b01e9c5b42e958c3c1e10132
Type: security-commit

## Details
release(runway): cherry-pick fix:  musd conversion flow selected payToken race condition (#41800)

- fix: cp-13.27.0 musd conversion flow selected payToken race condition
(#41762)

<!--
Please submit this PR as a draft initially.
Do not mark it as "Ready for review" until the template has been
completely filled out, and PR status checks have passed at least once.
-->

## **Description**

## Context

Users could reach the mUSD conversion confirmation with the wrong **Pay
with** token (for example native ETH) when entering from certain entry
points (for example a tertiary CTA). Automatic pay-token selection could
run when a persisted or flow-default token should already be fixed.

## Problem

- **`updateTransactionPaymentToken`** could race with other updates,
leading to the wrong token being stored or applied for the confirmation.
- **`MusdConversionInfo`** did not always disable automatic pay-token
selection when a **preferred** token was already known (persisted
controller state or flow default), so **Pay with** could be overwritten.

## Solution

- **Transaction pay token:** Address the race so the token written for
the transaction matches the intended one (related change on this
branch).
- **`MusdConversionInfo`:**
- Build **`preferredToken`** from the persisted token first, then from
**`useMusdConversionTokens`** **`defaultPaymentToken`** when nothing is
persisted.
- Set **`disablePay={Boolean(preferredToken)}`** on
**`CustomAmountInfo`** so **`useAutomaticTransactionPayToken`** does not
override when a preferred token exists.

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

CHANGELOG entry: Fixed incorrect pay token on the mUSD conversion
confirmation when opening the flow from CTAs

## **Related issues**

Fixes: https://consensyssoftware.atlassian.net/browse/MUSD-662
Fixes: https://github.com/MetaMask/metamask-extension/issues/41704

## **Manual testing steps**

```
Feature: mUSD conversion confirmation — Pay with token

  Background:
    Given the user is on the mUSD conversion confirmation screen
    And the transaction is an mUSD conversion

  Scenario: Pay with stays on persisted token
    Given a payment token is already stored in TransactionPay state for this transaction
    When the confirmation screen loads
    Then automatic pay-token selection must not replace that token
    And the UI must use that token as the preferred pay token

  Scenario: Pay with uses default token when none is persisted
    Given no payment token is stored for this transaction in TransactionPay state
    And the mUSD conversion flow exposes a default payment token
    When the confirmation screen loads
    Then the default payment token must be used as the preferred pay token
    And automatic pay-token selection must not pick a different token (e.g. native ETH)

  Scenario: Automatic selection allowed when no preferred token exists
    Given no payment token is persisted for this transaction
    And there is no default payment token for this flow
    When the confirmation screen loads
    Then automatic pay-token selection may run as usual

  Scenario: Navigation trace includes payment token context
    When the mUSD conversion confirmation info mounts
    Then a MusdConversionNavigation trace ends with payment token chain and address
    And unknown placeholders are used when no token is available yet
```
## **Screenshots/Recordings**

<!-- If applicable, add screenshots and/or recordings to visualize the
before and after of your change. -->

### **Before**

https://www.loom.com/share/33e0251d22734db0aa62cdd46347a44c

<!-- [screenshots/recordings] -->

### **After**

https://www.loom.com/share/131d3de840124939a6d5b2abaaa5b763

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
> **Medium Risk**
> Changes payment-token selection behavior for mUSD conversion
confirmations and the transaction-pay controller update timing, which
could affect which token is preselected/persisted in the pay flow if
edge cases were missed.
> 
> **Overview**
> Fixes a race in the mUSD conversion start flow by `await`ing
`updateTransactionPaymentToken` after navigation so the intended pay
token is reliably persisted for the new transaction.
> 
> Updates confirmation UI token-selection logic: `CustomAmountInfo`
gains `disableAutomaticToken` (disables
`useAutomaticTransactionPayToken`), and `MusdConversionInfo` now derives
`preferredToken` from persisted TransactionPay state or the flow’s
`defaultPaymentToken` and always disables automatic selection to prevent
overwrites. Tests are updated/added to cover these scenarios, including
unknown-token tracing and skeleton rendering when the pay token is not
yet set.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit
ecda23a51e9ba9662e5c3c6affdd0993a141bb6c. Bugbot is set up for automated
code reviews on this repo. Configure
[here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->
[754f085](https://github.com/MetaMask/metamask-extension/commit/754f0855feede5d0cf2f0cab68efe24c6b77985f)

Co-authored-by: Nicholas Smith <nick.smith@consensys.net>

### ui/hooks/musd/useMusdConversion.ts
```diff
@@ -286,7 +286,7 @@ export function useMusdConversion(): UseMusdConversionResult {
         });
 
         if (preferredToken?.address) {
-          updateTransactionPaymentToken({
+          await updateTransactionPaymentToken({
             transactionId: txId,
             tokenAddress: preferredToken.address as `0x${string}`,
             chainId,
```

### ui/pages/confirmations/components/info/custom-amount-info/custom-amount-info.test.tsx
```diff
@@ -89,6 +89,7 @@ const DEFAULT_ALERTS_HOOK_RETURN = {
 
 function render({
   hasMax = false,
+  disableAutomaticToken,
   disablePay = false,
   availableTokens = [MOCK_AVAILABLE_TOKEN],
   customAmountHookReturn = DEFAULT_CUSTOM_AMOUNT_HOOK_RETURN,
@@ -100,6 +101,7 @@ function render({
   requiredTokens = [],
 }: {
   hasMax?: boolean;
+  disableAutomaticToken?: boolean;
   disablePay?: boolean;
   availableTokens?: (typeof MOCK_AVAILABLE_TOKEN)[];
   customAmountHookReturn?: typeof DEFAULT_CUSTOM_AMOUNT_HOOK_RETURN;
@@ -162,7 +164,11 @@ function render({
   const state = getMockConfirmStateForTransaction(MOCK_TRANSACTION_META);
 
   return renderWithConfirmContextProvider(
-    <CustomAmountInfo hasMax={hasMax} disablePay={disablePay} />,
+    <CustomAmountInfo
+      hasMax={hasMax}
+      disableAutomaticToken={disableAutomaticToken}
+      disablePay={disablePay}
+    />,
     mockStore(state),
   );
 }
@@ -177,6 +183,39 @@ describe('CustomAmountInfo', () => {
     expect(getByTestId('custom-amount')).toBeInTheDocument();
   });
 
+  it('calls useAutomaticTransactionPayToken with disable false when both props unset', () => {
+    render();
+    expect(
+      useAutomaticTransactionPayTokenModule.useAutomaticTransactionPayToken,
+    ).toHaveBeenCalledWith(
+      expect.objectContaining({
+        disable: false,
+      }),
+    );
+  });
+
+  it('calls useAutomaticTransactionPayToken with disable true when disableAutomaticToken is true', () => {
+    render({ disableAutomaticToken: true });
+    expect(
+      useAutomaticTransactionPayTokenModule.useAutomaticTransactionPayToken,
+    ).toHaveBeenCalledWith(
+      expect.objectContaining({
+        disable: true,
+      }),
+    );
+  });
+
+  it('calls useAutomaticTransactionPayToken with disable true when disablePay is true', () => {
+    render({ disablePay: true });
+    expect(
+      useAutomaticTransactionPayTokenModule.useAutomaticTransactionPayToken,
+    ).toHaveBeenCalledWith(
+      expect.objectContaining({
+        disable: true,
+      }),
+    );
+  });
+
   it('renders pay token amount when disablePay is false', () => {
     const { getByTestId } = render({ disablePay: false });
     expect(getByTestId('pay-token-amount')).toBeInTheDocument();
```

### ui/pages/confirmations/components/info/custom-amount-info/custom-amount-info.tsx
```diff
@@ -48,6 +48,13 @@ import { useConfirmContext } from '../../../context/confirm';
 export type CustomAmountInfoProps = {
   children?: ReactNode;
   currency?: string;
+  /**
+   * When true, it prevents automatic selection of payment token based on balance and feature flags
+   */
+  disableAutomaticToken?: boolean;
+  /**
+   * When true, it disables MetaMask Pay for transactions that just need custom amount input
+   */
   disablePay?: boolean;
   hasMax?: boolean;
   preferredToken?: SetPayTokenRequest;
@@ -59,14 +66,15 @@ export const CustomAmountInfo: React.FC<CustomAmountInfoProps> = React.memo(
   ({
     children,
     currency,
+    disableAutomaticToken,
     disablePay,
     hasMax,
     overrideBottomContent,
     overrideCenterContent,
     preferredToken,
   }) => {
     useAutomaticTransactionPayToken({
-      disable: disablePay,
+      disable: Boolean(disablePay) || Boolean(disableAutomaticToken),
       preferredToken,
     });
     useTransactionPayMetrics();
```

### ui/pages/confirmations/components/info/musd-conversion-info/musd-conversion-info.test.tsx
```diff
@@ -11,6 +11,7 @@ import * as useTransactionPayMetricsModule from '../../../hooks/pay/useTransacti
 import * as useTransactionPayAvailableTokensModule from '../../../hooks/pay/useTransactionPayAvailableTokens';
 import * as useTransactionPayDataModule from '../../../hooks/pay/useTransactionPayData';
 import * as useTransactionPayTokenModule from '../../../hooks/pay/useTransactionPayToken';
+import * as useMusdConversionTokensModule from '../../../../../hooks/musd';
 import { MusdConversionInfo } from './musd-conversion-info';
 
 const mockEndTrace = jest.fn();
@@ -33,6 +34,12 @@ jest.mock('../../../hooks/pay/useTransactionPayMetrics');
 jest.mock('../../../hooks/pay/useTransactionPayAvailableTokens');
 jest.mock('../../../hooks/pay/useTransactionPayData');
 jest.mock('../../../hooks/pay/useTransactionPayToken');
+jest.mock('../../../hooks/musd/useMusdConversionQuoteTrace', () => ({
+  useMusdConversionQuoteTrace: jest.fn(),
+}));
+jest.mock('../../../../../hooks/musd', () => ({
+  useMusdConversionTokens: jest.fn(),
+}));
 
 jest.mock('./musd-override-content', () => ({
   MusdOverrideContent: ({ amountHuman }: { amountHuman: string }) => (
@@ -72,6 +79,16 @@ jest.mock('../../rows/claimable-bonus-row/claimable-bonus-row', () => ({
 const MOCK_TRANSACTION_META =
   genUnapprovedContractInteractionConfirmation() as TransactionMeta;
 
+const PERSISTED_PAYMENT_TOKEN = {
+  address: '0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
+  chainId: '0x14a33' as const,
+};
+
+const DEFAULT_HOOK_PAYMENT_TOKEN = {
+  address: '0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
+  chainId: '0x1' as const,
+};
+
 const MOCK_AVAILABLE_TOKEN = {
   address: '0x123' as const,
   chainId: '0x1' as const,
@@ -89,10 +106,15 @@ function setupDefaultMocks({
   isQuotesLoading = false,
   hasQuotes = false,
   hideResults = false,
+  defaultPaymentToken = null as {
+    address: string;
+    chainId: `0x${string}`;
+  } | null,
 }: {
   isQuotesLoading?: boolean;
   hasQuotes?: boolean;
   hideResults?: boolean;
+  defaultPaymentToken?: { address: string; chainId: `0x${string}` } | null;
 } = {}) {
   jest
     .mocked(useTransactionCustomAmountModule.useTransactionCustomAmount)
@@ -148,12 +170,32 @@ function setupDefaultMocks({
       payToken: undefined,
       setPayToken: jest.fn(),
     });
+  jest
+    .mocked(useMusdConversionTokensModule.useMusdConversionTokens)
+    .mockReturnValue({
+      filterAllowedTokens: (tokens) => tokens,
+      filterTokens: (tokens) => tokens,
+      isConversionToken: () => false,
+      isMusdSupportedOnChain: () => false,
+      hasConvertibleTokensByChainId: () => false,
+      tokens: [],
+      defaultPaymentToken,
+    });
 }
 
-function render(mockOptions: Parameters<typeof setupDefaultMocks>[0] = {}) {
+type MockConfirmStateArgs = NonNullable<
+  Parameters<typeof getMockConfirmStateForTransaction>[1]
+>;
+
+function render(
+  mockOptions: Parameters<typeof setupDefaultMocks>[0] = {},
+  stateArgs?: MockConfirmStateArgs,
+) {
   setupDefaultMocks(mockOptions);
 
-  const state = getMockConfirmStateForTransaction(MOCK_TRANSACTION_META);
+  const state = stateArgs
+    ? getMockConfirmStateForTransaction(MOCK_TRANSACTION_META, stateArgs)
+    : getMockConfirmStateForTransaction(MOCK_TRANSACTION_META);
 
   return renderWithConfirmContextProvider(
     <MusdConversionInfo />,
@@ -167,16 +209,38 @@ describe('MusdConversionInfo', () => {
     mockEndTrace.mockClear();
   });
 
-  it('ends navigation trace with paymentTokenChainId and paymentTokenAddress on mount', () => {
+  it('ends navigation trace with unknown payment token when none is persisted', () => {
     render();
 
     expect(mockEndTrace).toHaveBeenCalledWith(
       expect.objectContaining({
         name: 'MusdConversionNavigation',
-        data: expect.objectContaining({
-          paymentTokenChainId: expect.any(String),
-          paymentTokenAddress: expect.any(String),
-        }),
+        data: {
+          paymentTokenChainId: 'unknown',
+          paymentTokenAddress: 'unknown',
+        },
+      }),
+    );
+  });
+
+  it('ends navigation trace with persisted payment token from TransactionPay state', () => {
+    render(undefined, {
+      metamask: {
+        transactionData: {
+          [MOCK_TRANSACTION_META.id]: {
+            paymentToken: PERSISTED_PAYMENT_TOKEN,
+          },
+        },
+      },
+    });
+
+    expect(mockEndTrace).toHaveBeenCalledWith(
+      expect.objectContaining({
+        name: 'MusdConversionNavigation',
+        data: {
+          paymentTokenChainId: PERSISTED_PAYMENT_TOKEN.chainId,
+          paymentTokenAddress: PERSISTED_PAYMENT_TOKEN.address,
+        },
       }),
     );
   });
@@ -194,6 +258,63 @@ describe('MusdConversionInfo', () => {
     expect(getByTestId('musd-override-content')).toHaveTextContent('50');
   });
 
+  describe('preferredToken and automatic transaction pay token', () => {
+    it('calls useAutomaticTransactionPayToken with disable true when no preferred token', () => {
+      render();
+
+      expect(
+        useAutomaticTransactionPayTokenModule.useAutomaticTransactionPayToken,
+      ).toHaveBeenCalledWith(
+        expect.objectContaining({
+          disable: true,
+          preferredToken: undefined,
+        }),
+      );
+    });
+
+    it('calls useAutomaticTransactionPayToken with disable true and token from TransactionPay state', () => {
+      render(undefined, {
+        metamask: {
+          transactionData: {
+            [MOCK_TRANSACTION_META.id]: {
+              paymentToken: PERSISTED_PAYMENT_TOKEN,
+            },
+          },
+        },
+      });
+
+      expect(
+        useAutomaticTransactionPayTokenModule.useAutomaticTransactionPayToken,
+      ).toHaveBeenCalledWith(
+        expect.objectContaining({
+          disable: true,
+          preferredToken: {
+            address: PERSISTED_PAYMENT_TOKEN.address,
+            chainId: PERSISTED_PAYMENT_TOKEN.chainId,
+          },
+        }),
+      );
+    });
+
+    it('calls useAutomaticTransactionPayToken with disable true and default payment token when not persisted', () => {
+      render({
+        defaultPaymentToken: DEFAULT_HOOK_PAYMENT_TOKEN,
+      });
+
+      expect(
+        useAutomaticTransactionPayTokenModule.useAutomaticTransactionPayToken,
+      ).toHaveBeenCalledWith(
+        expect.objectContaining({
+          disable: true,
+          preferredToken: {
+            address: DEFAULT_HOOK_PAYMENT_TOKEN.address as `0x${string}`,
+            chainId: DEFAULT_HOOK_PAYMENT_TOKEN.chainId,
+          },
+        }),
+      );
+    });
+  });
+
   describe('MusdBottomContent', () => {
     it('renders bottom content rows when quotes are loading', () => {
       const { getByTestId } = render({ isQuotesLoading: true });
```

### ui/pages/confirmations/components/info/musd-conversion-info/musd-conversion-info.tsx
```diff
@@ -1,5 +1,8 @@
-import type { TransactionMeta } from '@metamask/transaction-controller';
-import React, { useCallback, useEffect, useRef } from 'react';
+import {
+  TransactionType,
+  type TransactionMeta,
+} from '@metamask/transaction-controller';
+import React, { useCallback, useEffect, useMemo, useRef } from 'react';
 import { useSelector } from 'react-redux';
 import { Box, BoxFlexDirection } from '@metamask/design-system-react';
 import { endTrace, TraceName } from '../../../../../../shared/lib/trace';
@@ -15,6 +18,7 @@ import {
   useIsTransactionPayLoading,
   useTransactionPayQuotes,
 } from '../../../hooks/pay/useTransactionPayData';
+import { useMusdConversionTokens } from '../../../../../hooks/musd';
 import { BridgeFeeRow } from '../../rows/bridge-fee-row/bridge-fee-row';
 import { ClaimableBonusRow } from '../../rows/claimable-bonus-row/claimable-bonus-row';
 import { TotalRow } from '../../rows/total-row/total-row';
@@ -86,9 +90,25 @@ export const MusdConversionInfo = () => {
     }
   }, [existingPayToken?.chainId, existingPayToken?.address, transactionId]);
 
-  const preferredToken = existingPayToken
-    ? { address: existingPayToken.address, chainId: existingPayToken.chainId }
-    : undefined;
+  const { defaultPaymentToken } = useMusdConversionTokens({
+    transactionType: TransactionType.musdConversion,
+  });
+
+  const preferredToken = useMemo(() => {
+    if (existingPayToken) {
+      return {
+        address: existingPayToken.address,
+        chainId: existingPayToken.chainId,
+      };
+    }
+    if (defaultPaymentToken) {
+      return {
+        address: defaultPaymentToken.address as `0x${string}`,
+        chainId: defaultPaymentToken.chainId,
+      };
+    }
+    return undefined;
+  }, [defaultPaymentToken, existingPayToken]);
 
   const renderOverrideContent = useCallback(
     (amountHuman: string) => <MusdOverrideContent amountHuman={amountHuman} />,
@@ -97,7 +117,7 @@ export const MusdConversionInfo = () => {
 
   return (
     <CustomAmountInfo
-      disablePay={Boolean(existingPayToken)}
+      disableAutomaticToken={true}
       preferredToken={preferredToken}
       overrideCenterContent={renderOverrideContent}
       overrideBottomContent={<MusdBottomContent />}
```

### ui/pages/confirmations/components/info/musd-conversion-info/musd-override-content.test.tsx
```diff
@@ -1,5 +1,6 @@
 import React from 'react';
 import { render, screen } from '@testing-library/react';
+import type { TransactionPaymentToken } from '@metamask/transaction-pay-controller';
 
 import { useCustomAmount } from '../../../../../hooks/musd/useCustomAmount';
 import { useTransactionPayAvailableTokens } from '../../../hooks/pay/useTransactionPayAvailableTokens';
@@ -36,14 +37,47 @@ const mockUseTransactionPayAvailableTokens =
 const mockUseTransactionPayToken =
   useTransactionPayToken as jest.MockedFunction<typeof useTransactionPayToken>;
 
+const MOCK_PAY_TOKEN: TransactionPaymentToken = {
+  address: '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
+  chainId: '0x1',
+  symbol: 'USDC',
+  decimals: 6,
+  balanceFiat: '100',
+  balanceHuman: '100',
+  balanceRaw: '100000000',
+  balanceUsd: '100',
+};
+
 describe('MusdOverrideContent', () => {
   beforeEach(() => {
     jest.clearAllMocks();
     mockUseTransactionPayToken.mockReturnValue({
-      payToken: { address: '0xabc', chainId: '0x1' } as unknown as ReturnType<
-        typeof useTransactionPayToken
-      >['payToken'],
+      payToken: MOCK_PAY_TOKEN,
       setPayToken: jest.fn(),
+      isNative: false,
+    });
+  });
+
+  describe('when tokens are available but no pay token is pre-selected', () => {
+    it('renders PayWithRowSkeleton until controller pay token is set', () => {
+      mockUseCustomAmount.mockReturnValue({
+        shouldShowOutputAmountTag: false,
+        outputAmount: null,
+        outputSymbol: null,
+      });
+      mockUseTransactionPayAvailableTokens.mockReturnValue([
+        { symbol: 'USDC', chainId: '0x1' },
+      ] as ReturnType<typeof useTransactionPayAvailableTokens>);
+      mockUseTransactionPayToken.mockReturnValue({
+        payToken: undefined,
+        setPayToken: jest.fn(),
+        isNative: false,
+      });
+
+      render(<MusdOverrideContent amountHuman="0" />);
+
+      expect(screen.getByTestId('pay-with-row-skeleton')).toBeInTheDocument();
+      expect(screen.queryByTestId('pay-with-row')).not.toBeInTheDocument();
     });
   });
 
```

### ui/pages/confirmations/hooks/pay/useAutomaticTransactionPayToken.test.tsx
```diff
@@ -66,7 +66,11 @@ function renderHookWithProvider({
   );
 
   return renderHook(
-    () => useAutomaticTransactionPayToken({ disable, preferredToken }),
+    () =>
+      useAutomaticTransactionPayToken({
+        disable,
+        preferredToken,
+      }),
     { wrapper },
   );
 }
```
