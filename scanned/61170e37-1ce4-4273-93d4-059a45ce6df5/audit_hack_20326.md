# [C] **5.1.1 Side effects of LTV = 0 assets: Morpho's users will not be able to withdraw (collateral and "pure"

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
supply), borrow and liquidate**

**Severity:** Critical Risk

**Context:** PositionsManager.sol#L120-L121, PositionsManager.sol#L180, PositionsManager.sol#L213, Positions-
Manager.sol#L

**Description:** When an AToken hasLTV = 0, Aave restricts the usage of some operations. In particular, if the user
owns at least one AToken as collateral that hasLTV = 0, operations could revert.

```
1) Withdraw: if the asset withdrawn is collateral, the user is borrowing something, the operation will revert if the
withdrawn collateral is an AToken withLTV > 0.
2) Transfer: if thefromis using the asset as collateral, is borrowing something and the asset transferred is an
AToken withLTV > 0the operation will revert.
3) Set the reserve of an AToken as not collateral: if the AToken you are trying to set as non-collateral is an
AToken withLTV > 0the operation will revert.
```
Note that all those checks are done on top of the "normal" checks that would usually prevent an operation, de-
pending on the operation itself (like, for example, an HF check).

While a "normal" Aave user could simply withdraw, transfer or set that asset as non-collateral, Morpho, with the
current implementation, cannot do it. Because of the impossibility to remove from the Morpho wallet the "poisoned
AToken", part of the Morpho mechanics will break.

- Morpho's users could not be able to withdraw both collateral and "pure" supply
- Morpho's users could not be able to borrow
- Morpho's users could not be able to liquidate
- Morpho's users could not be able to claim rewards viaclaimRewardsif one of those rewards is anAToken
    withLTV > 0

**Recommendation:** Morpho should avoid listing as marketsATokens withLTV = 0orATokens that soon will be
LTV = 0.

In case Morpho has already created markets for tokens that will be configured withLTV = 0a well-detailed and
tested procedure to reach a state that prevents the listed side effects should be applied as soon as possible.

The final goal of Morpho should be to arrive at a point where those markets are

- Paused.
- Have no supplied/borrow balance owned by the users.
- Have only 1 wei of collateral balance owned by Morpho.
- Have the reserve set as non-collateral while remaining overall healthy.

The last two points are to avoid possible griefing attacks.

**Morpho:** Fixed in PR 569.

**Spearbit:** The fix implements a mechanism that allows Morpho to set an asset as collateral/not collateral on
Morpho and Aave. This implementation is needed to handle the edge case where an asset LTV is set to zero by
the Aave Governance.

Without setting an LTV = 0 asset as non-collateral on Aave, some core mechanics of Morpho's protocol would
break. While this PR solve this specific issue, all the side effects described in the issue still remain true.


When an asset is set toisCollateral = falseon Morpho or hasLTV = 0on Aave, Morpho's user's LTV and HF
will be reduced because Morpho is treating that asset not as collateral anymore. The behavior has the following
consequences for Morpho's users:

- User could not be able to borrow anymore (because of reduced LTV).
- User could not be able to withdraw anymore (because of reduced HF).
- User could be liquidable (because of reduced HF).
- Increase the possibility, in case of liquidation, to liquidate the whole debtor's collateral (because of reduced
    HF).
- While the asset is not threaded as collateral anymore, it can still be sized during the liquidation process.

Note that in case LTV = 0, the same user on Aave would have a different situation because on Aave, in this specific
scenario, only the LTV is reduced and not the HF.

The PR is lacking documentation of this behavior and the differences between Morpho and Aave in this scenario.
The PR is also lacking a well-documented procedure that the users should follow both before and after the LTV
= 0 edge case to avoid being liquidated or incur in any of those side effects once Morpho's has set the asset as
not-collateral or Aave has set the LTV to zero.

Because the PR does not solve the user's side effects, Morpho should consider documenting them and provide
a well-documented procedure that the users should follow for the issue's scenario. Morpho should also consider
implementing some UI/UX mechanism that properly alerts users to take those actions for assets that will soon be
set toisCollateral = falseon Morpho orLTV = 0on Aaave.
