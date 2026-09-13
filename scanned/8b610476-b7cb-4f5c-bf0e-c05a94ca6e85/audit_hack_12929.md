# [H] Malicious keeper can completely manipulate the funds that a user gets on their spot orders causing them a loss of funds

## Summary
Severity: High
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L82-L116
Type: audit-issue

## Details
# Malicious keeper can completely manipulate the funds that a user gets on their spot orders causing them a loss of funds

## Summary
Malicious keeper can completely manipulate the funds that a user gets on their spot orders causing them a loss of funds

## Vulnerability Detail
Currently keepers have the power to execute both `dca` and `limit` orders by calling the respective functions like `execute_dca_order`

The problem with these functions to execute orders is that as they lack access control, anyone can do as keeper when the parameters are met. 

The only way to do it is that the keeper has the change to choose the swap path that the order will go through to swap to the respective token:

`def execute_dca_order(_uid: bytes32, _uni_hop_path: DynArray[address, 3], _uni_pool_fees: DynArray[uint24, 2], _share_profit: bool):`

The malicious keeper can monitor what the `amountMinOut` calculated/specified is and pass a very iliquid/high fees paths through where the swap will go through.

Scenario for limit orders:

- User creates an order to swap 2000USDC for 1 ETH, 1 ETH as the minAmountOut
- Order can be executed because it meets  the parameters.
- Market fluctuates and the user will actually receive 1.02 ETH for 2000 USDC.
- Malicious keeper executes order will a very iliquid/high fees pools in the `path` param. After the execution the swap was performed and user received the exact amounMin = 1ETH for 2000USDC, with an unrealized loss of .02 ETH.


## Impact
Allowing anyone to execute orders, will make users loss funds 

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L82-L116
## Tool used

Manual Review

## Recommendation
Add an access control to execute orders, only internal keepers should be the one to execute them.
