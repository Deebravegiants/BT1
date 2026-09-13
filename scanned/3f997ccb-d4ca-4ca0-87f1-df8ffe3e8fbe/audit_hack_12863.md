# [H] Attacker can DoS Margin DEX by leaving bad debt

## Summary
Severity: High
Reporter: Tricko
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L232-L279
Type: audit-issue

## Details
# Attacker can DoS Margin DEX by leaving bad debt

## Summary
By calling `close_trade()` with a low `_min_amount_out` and sandwiching his own transaction, an attacker can create bad debt and as a consequence set `self.is_accepting_new_orders = False`, thus blocking all future `open_trade()` calls until admin intervention.

## Vulnerability Detail
When closing his trade, the user supplies the `_min_amount_out` argument that control the minimum amount necessary to be received from the swap in order for the call to succeed. An attacker can set a deliberately small `_min_amount_out` while also sandwiching his own `close_position` transaction to result in a very low `amount_out_received` from the swap. This enable the attacker to cause bad debt in the vault at will, making `self.is_accepting_new_orders = False` and therefore blocking new orders.

By doing all in one transaction, the attacker can make sure he controls the pool state before the swap done by the `Vault`. Using the funds obtained from a flashloan he can make a big swap in the pool, making it unbalanced enough to guarantee that when the `Vault` swap happens, it will result in a small enough `amount_out_received` to leave bad debt (`amount_out_received < position_debt_amount`). 

Attack reproduction steps, done in a single transaction.
1. Create a trade using `open_trade()` DAI -> USDC
2. Get a flashloan
3. Big swap from USDC to DAI, unbalancing the selected DAI/USDC pool.
4. Close his position by calling `close_trade()` with `_min_amount_out = 1`
5. Swap from DAI to USDC (to recover the funds and being able to repay the flashloan)
6. Repay the flashloan

The swap done during `close_trade()` in step 4 will occur on a unabalnced DAI/USDC pool, resulting in small `amount_out_received`. The attacker can control exactly the value of `amount_out_received` by sizing the first swap done in the sandwich. Because `_min_amount_out` (controlled by the attacker) is small, this swap succeds regardless of the high slippage. As a consequence the `amount_out_received` is not enough to pay the position debt, making the `Vault` enter defensive mode (`self.is_accepting_new_orders = False`) and blocking future new orders. 

As the `Vault` will enter defensive mode regardless of the amount of bad debt, the attacker can set this attack using small sized trades. Additionally, by assuming the role of the sandwicher during the high slippage swap, they can reclaim a substantial portion of the his margin funds. Consequently, the overall funds required for this attack remain minimal, enabling the attacker to repeat it indefinitely.

## Impact
The attacker can cause bad debt at will, triggering the defensive mode and blocking the DEX from accepting new orders. Even if the protocol admins enable `open_trade()` again, the attacker can keep repeating the attack to DoS the DEX indefinitely.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L232-L279

## Tool used
Manual Review

## Recommendation
Consider checking if the user supplied `_min_amount_out` is equal ou above the `_market_order_min_amount_out` and revert otherwise.
