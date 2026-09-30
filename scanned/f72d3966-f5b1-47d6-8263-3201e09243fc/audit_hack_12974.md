# [H] TakeProfit and StopLoss execution does not factor in slippage or sudden price movements

## Summary
Severity: High
Reporter: seerether
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L371-L449
Type: audit-issue

## Details
# TakeProfit and StopLoss execution does not factor in slippage or sudden price movements

## Summary
The execution of TakeProfit (execute_tp_order) and StopLoss (execute_sl_order) orders seems to rely on an external entity calling these functions to trigger them. The code does not check for the current market conditions or use an automated mechanism to execute these orders, which could lead to inefficiencies or unexpected outcomes.
## Vulnerability Detail
The execute_tp_order  and execute_sl_order function checks if the trigger price is higher than the current exchange rate, but it does not consider factors such as slippage or sudden price movements. This lack of validation can result in premature execution or missed execution opportunities.
By relying on external entities to trigger the execution, there is a potential for delays or manipulation by malicious actors, leading to unexpected outcomes or financial losses
## Impact
Orders can be executed even if the market conditions are unfavorable, leading to potential losses if the execution happens at an undesirable price level.
Relying on manual execution introduces the risk of delays or missed execution opportunities, especially in fast-moving markets, which can result in significant financial losses.
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L371-L449
## Tool used

Manual Review

## Recommendation
implement an automated mechanism that periodically checks the current market conditions and triggers the execution of TP and SL orders based on predefined criteria.
Introduce a new function called check_orders that will be responsible for checking the market conditions and executing the take profit and stop loss orders if the criteria are met
https://github.com/seerether/Unstoppable/blob/main/unstoppablemitigate1
Modify the execute_tp_order and execute_sl_order functions to include a modifier that checks whether the caller is the automated mechanism calling the check_orders function.
https://github.com/seerether/Unstoppable/blob/main/unstoppablemitigate1a
Implement a mechanism to call the check_orders function periodically. This can be done using external tools like cron jobs, or you can integrate it into your existing system based on your deployment environment.
