# [M] Limit Orders in the Spot-Dex can be re-executed by anyone without any limit which can affect the execution of all the other Limit Orders for the users

## Summary
Severity: Medium
Reporter: 0xStalin
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L187-L189
Type: audit-issue

## Details
# Limit Orders in the Spot-Dex can be re-executed by anyone without any limit which can affect the execution of all the other Limit Orders for the users

## Summary
- Limit Orders in the Spot-Dex can be re-executed 

## Vulnerability Detail
- First of all, let's understand what a Limit Order is, as per [invertor.gov](https://www.investor.gov/introduction-investing/investing-basics/how-stock-markets-work/types-orders#:~:text=A%20limit%20order%20is%20an,for%20no%20more%20than%20%2410.):
  - **A limit order is an order to buy or sell a security at a specific price or better.** 
    - ***A buy limit order can only be executed at the limit price or lower***
    - ***A sell limit order can only be executed at the limit price or higher.***

- From the above definition it can be understood that Limit Orders should be executed only once when the buy/sell conditions are met.

- Now, the impact on the protocol (apart from making the Limit Orders not behave at 100% as Limit Orders) is that malicious actors can re-execute the same Limit Order in search of claiming the profit for executing a user's Limit Order, which will cause the contract & user's balances & allowances to be updated and not matching the required state to execute the rest of the user Limit Orders.

- Basically, malicious users can always receive a profit from executing Limit Orders because the variable `_share_profit` is received as an argument, so, malicious actors have the incentive to re-execute as many times as the order's owner can handle (in the sense of having enough token's balance and the contract having enough allowance) the order's execution, because [they'll get the 50% of the profit that the protocol is making](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L187-L189)
  - Suppose the next scenario: 
    - A user has created 10 different Limit Orders using the same token_in & exactly the same amount_in on all of those orders
    - Because all those 10 Limit Orders were created it means that the LimitOrder contracts have 10 times the amount_in of allowance to spend on behalf of the order owner.
    - Now, a malicious actor re-executes 10 times Order 1 & get's away with the commissions, but now the state of the contract and the owner account has been changed:
      - Now the contract doesn't have enough allowance on the order's owner account & probably also the owner won't have enough `token_in` to execute the other 9 orders
    
  - Malicious actors can continue to exploit the same order while the order is not deleted or it has not expired.
    - During all this time, the rest of the owner's orders won't be able to be executed
  - When the owner's orders delete the order being exploited, the malicious actors can simply shift to another order and perform the same steps to keep extracting value from the profits.

- Basically, the Limit Orders can be exploited until users give up on trying to prevent malicious actors from affecting their posted limit orders and users might end up not using the feature.

## Impact
- Re-executing multiple times the same Limit Order can cause the rest of the User Limit Orders to not be able to be executed because the contract & user's state has been altered (balances & allowances)

## Code Snippet
- [LimitOrders::execute_limit_order()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L130-L191)

## Tool used
Manual Review

## Recommendation
- I can think of a number of different approaches to mitigate this issue:
  - Allow Limit Orders to be executed only once
  - Set the `_share_profit` argument as a contract variable, so, malicious actors are discouraged from persisting to re-execute the Limit Orders
  - Restrict who can execute the limit orders
