# [M] Unauthorized increase of `maxSellPercent`

## Summary
Severity: Medium
Contest weight: 0.2660
Dataset id: 22357
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an unauthorized increase of the maximum sell percentage (maxSellPercent) in the vesting manager, allowing token holders to sell tokens even after the token issuer explicitly disabled selling by setting maxSellPercent to zero. The root cause is a flawed initialization check in the setSellable function: when maxSellPercent equals zero the function treats the value as uninitialized and automatically assigns a default limit of 20% together with default sellFee and buyFee values. Consequently, any later call to setSellable—typically performed by an admin to relist a vesting after a temporary issue—overwrites the issuer’s zero limit with the default 20% without any additional permission check. An attacker or even an honest admin can therefore trigger the bug simply by toggling the sellable flag after the issuer has set maxSellPercent to zero. The impact is that users can unexpectedly sell vested tokens, violating the business rule that the issuer intended to enforce, potentially leading to market disruption, loss of control over token distribution, and financial loss for the issuer. The condition occurs only when the issuer first sets maxSellPercent to zero and later the admin calls setSellable, which the contract mistakenly interprets as a first‑time initialization. Both token holders and the token issuer are affected: holders see the ability to sell when they expect a lock, and the issuer loses the intended restriction. The issue was discovered during a Code4rena audit and confirmed by the project maintainer. It is hard to notice because the UI may still indicate that the vesting is listed, and the change to the sell limit happens silently in the background, making the unexpected sell capability appear as a normal operation. To remediate the problem, the contract should track whether the vesting parameters have been initialized—e.g., by adding an ‘initiated’ flag—and only allow setSellable to modify maxSellPercent when the vesting has not yet been initialized, or otherwise prevent the function from overwriting an existing non‑zero limit. This change ensures that the issuer’s explicit zero limit cannot be overridden unintentionally, preserving the intended accounting and sell‑restriction logic.

## Proof of Concept
The `SecondSwap_VestingManager` contract manages vesting settings and allocations for tokens. A critical function in this context is `setMaxSellPercent`, which allows the `tokenIssuer` to set the maximum percentage of vesting tokens that can be sold by users. 

The issue arises from the interaction between the `setSellable` and `setMaxSellPercent` functions. When the `tokenIssuer` sets `maxSellPercent` to 0 to prevent selling, the following sequence of events can occur:

  1. The token issuer calls `setMaxSellPercent(vesting, 0)` to prevent any selling of their tokens.
  2. Because an issue with the vesting has occurred, the admin calls `setSellable(vesting, true)` to unlist the vesting 
  3. The issue gets fixed and the admin subsequently calls `setSellable(vesting, true)` again to list the vesting again. This inadvertently sets `maxSellPercent` to 20% because the current value is 0, which is interpreted as a lack of initialization.
  4. As a result, users can now sell their tokens, despite the issuer’s intention to prevent it.

This flaw allows the admin to accidentally override the issuer’s settings, leading to unauthorized selling of tokens.

It also sets the `sellFee` and `buyFee` back to default which might not be intended if the admit has changed them before.

## Recommendation
To mitigate this issue, a new variable `initiated` should be added to the vesting settings. This variable will track whether the vesting has been initialized. The `setSellable` function should only update the `maxSellPercent` if `initiated` is false which should only be when the vesting is initial created.

**bobwong (SecondSwap) confirmed**
