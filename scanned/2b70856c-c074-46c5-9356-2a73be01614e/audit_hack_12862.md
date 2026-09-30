# [H] `MarginDex` can be placed in DoS state via griefing attack

## Summary
Severity: High
Reporter: 0xyPhilic
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L264-L272
Type: audit-issue

## Details
# `MarginDex` can be placed in DoS state via griefing attack

## Summary

The `MarginDex` allows users to open leveraged positions on specified markets by combining a margin amount provided by the user and a debt amount provided by liquidity providers on the protocol. The `MarginDex` forwards execution to the `Vault` contract, which uses UniswapV3 pools under the hood to execute spot swaps. In order for users and liquidity providers to operate on the protocol the `is_accepting_new_orders` variable should be set to `true`. However an attacker can exploit the contract operations in order to place the `Vault` in a state of DoS where `is_accepting_new_orders` is `False`, thus rendering the following function unusable: `fund_account_eth`, `fund_account`, `provide_liquidity_eth`, `provide_liquidity` and `open_position`. 

## Vulnerability Detail

The vulnerability hides in the fact that accounting on the protocol does not take into consideration the swap fees paid on UniswapV3 pools when a spot swap is executed both during `open_position` and `close_position in regards to the `debt_amount`. There are a few steps to this attack which would finally trigger the [else logic](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L264-L272) that will place the `MarginDex` in DoS state by setting `is_accepting_new_orders` to `False`. The following steps lead to this state:
1) Attacker makes a call to `open_position` on the `MarginDex` to open a new margin position
2) Attacker makes a call to `reduce_position` with an amount that would leave his `margin_amount` close to 0 and will also reduce the overall `position.position_amount`
3) Attacker calls `close_trade` which after swapping the remaining `position.position_amount` falls in the `else` statement mentioned above causing a halt to the protocol

To understand better the issue let's illustrate it with an example. For the sake of example and simplicity I'll use DAI margin position with USDC (1:1 ratio), however the problem would occur on any position:

1/ `Open_position` is called with:
- margin_amount = 1
- debt_amount = 5
- debt_shares = 5e18 (assuming it is the first trade for simplicity)
- token_in_amount = 5 + 1 = 6
- amount_bought = 6 - (6 * 0.05%) = 5.997 (the pool through which the swap is executed has a 0.05% fee)

The final position data would be:

```vyper
{
            uid: position_uid, # position UID
            account: _account, # account of the attacker
            debt_token: _debt_token, # USDC
            margin_amount: _margin_amount, # 1
            debt_shares: debt_shares, # 5e18
            position_token: _position_token, # DAI
            position_amount: amount_bought, # 5.997
        }
```

2/ `Reduce_position` is called with `reduce_by_amount` = 5 as it needs to be lower or equal to `position_amount`

- debt_amount = 5 
- margin_debt_ratio = 0.2 --> 1 * 1e18 / 5
- amount_out_received = 5 - (5 * 0.05%) = 4.9975
- reduce_margin_by_amount = 4.9975 * 0.2 = 0.9995
- reduce_debt_by_amount = 4.9975 - 0.9995 = 3.998

Now:
- position.margin_amount = 1 - 0.9995 = 0.0005
- burnt_debt_shares = 3.998e18
- position.debt_shares = 5e18 - 3.998e18 = 1.002e18
- position.position_amount = 5.997 - 5 = 0.997

3/ `Close_position` is called

- position_debt_amount = 1.002
- amount_out_received = 0.997 - (0.997 * 0.05%) = 0.9965015

Then we have the check `if amount_out_received >= position_debt_amount` then everything is okey, however as we can see the `amount_out_received` is smaller than `position_debt_amount` thus the `else` is executed and `is_accepting_new_orders` is set to False, blocking the protocol.

The above steps can be executed within a single transaction so interest is not generated. Although the protocol admin has the option to reset the `is_accepting_new_orders` back to True, an attacker can perform the griefing attack immediatelly after that as the cost is very low and continue blocking the protocol for an infinite amount of time.

## Impact

Users and liquidity providers won't be able to operate properly on the protocol thus any funds provided by both parties will be locked for an infinite amount of time.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L264-L272

## Tool used

Manual Review

## Recommendation

Make sure to account for fees paid when swapping on UniswapV3 or any other DEX by adjusting the position_debt and maybe decreasing the user overall margin in the mapping.
