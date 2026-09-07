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

_Trimmed to 38 lines — full report: https://github.com/MetaMask/metamask-extension/commit/2fc2d8ba07773a78b01e9c5b42e958c3c1e10132_
