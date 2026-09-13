# [M] When a position is liquidated and BadDebt is generated because of the liquidation, the position's account is not penalized

## Summary
Severity: Medium
Reporter: 0xStalin
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L375
Type: audit-issue

## Details
# When a position is liquidated and BadDebt is generated because of the liquidation, the position's account is not penalized

## Summary
- When a position is liquidated and BadDebt is generated because of the liquidation, the position's account is not penalized

## Vulnerability Detail
- The account's margin (`self.margin[position.account][position.debt_token]`) is only penalized if the position being liquidated did not generate bad debt, but **when bad debt was indeed generated, the position's account is not penalized**

- Let's go through the liquidation process, so, if a position is liquidable, the [`Vault::liquidate()`](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L375) will call the [`Vault::_close_position()`](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233-L279), inside this function it will be executed a swap to cover the debt, and finally is validated if the received amount from the swap is greather than the position's debt
  - [If so](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L259-L263), it accrues the profit (the difference between the received tokens and the position's debt) to the position's account by increasing the margin and repays the debt.
  - [If the received amount is not enough to cover the debt](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L264-L272), the contract will pause new orders, generate badDebt and will try to repay as much as possible of the position's debt, **but the position's account margin is left untouched (in comparisson when a profit was make).**

- So, when the execution flow comes back from the `Vault::_close_position()` to the `Vault::liquidate()`, it [will compute how much penalty the account's position will be charged](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L365-L366) because of the liquidation, and then it validates if the received amount is greater than the position's debt:
  - [If the received amount was grater than the position's debt](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L368-L373) **(no bad debt was generated)**, the position's account will be charged a penalty that is deducted from its margin
  - But, if the received amount was not enough to cover the position's debt, or in other words, **if the liquidation generated bad debt**, ***the position's account is not being charged any penalty, its margin is left untouched***

- To make it fair for all the actors in the protocol, when bad debt is generated, the whole computed penalty should be charged to the position's account.

## Impact
- Not charging penalties to position's accounts when their positions generate bad debt won't really incentivize the position's owners to prevent their positions going underwater and cause bad debt for the protocol because their balances won't be affected if the position generates bad debt, also, LPs are putting at risk their liquidity, and if bad debt is generated, LPs are the ones who'll get a cut on their assets, is not fair that users who causes bad debt are not penalized.

## Code Snippet
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L365-L373

## Tool used
Manual Review

## Recommendation
- Make sure to penalize position's account when their positions are liquidated, despite if the position generated bad debt or not, otherwise, the position's account won't have any real consequence when their positions generate bad debt for the protocol
```solidity
def liquidate(_position_uid: bytes32):
    ...

    # penalize account
    penalty: uint256 = debt_amount * self.liquidation_penalty / PERCENTAGE_BASE

    if amount_out_received > debt_amount:
        # margin left
        remaining_margin: uint256 = amount_out_received - debt_amount
        penalty = min(penalty, remaining_margin)
        self.margin[position.account][position.debt_token] -= penalty
        self._distribute_trading_fee(position.debt_token, penalty)
+   # bad debt was generated!
+   else:
+     self.margin[position.account][position.debt_token] -= penalty

    ...
```
