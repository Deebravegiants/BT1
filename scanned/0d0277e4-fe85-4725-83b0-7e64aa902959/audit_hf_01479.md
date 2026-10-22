# [M] User will loose funds

## Summary
Severity: Medium
Contest weight: 0.6843
Dataset id: 7849
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a missing validation of the swap route length combined with an unchecked minimum‑output parameter, which allows a user to unintentionally lock or lose funds when calling the contract’s swap functions (swapForETH, swapWithETH, swapEntireBalance, or swap). The contract expects a multi‑hop route that describes how the input token should be exchanged for the output token. If a caller supplies a route array that contains only a single element – typically WETH – the internal loop that performs the swaps iterates from 0 to route.length‑1. With a length of one, the loop condition (i < route.length‑1) evaluates to false immediately, so no swap logic is executed. At the same time, the caller can set buy_amt_min (the minimum acceptable amount of output token) to zero, which is interpreted as “accept any amount, even none”. After the contract successfully pulls the user’s input tokens (pay_amt plus the market fee) via ERC20.transferFrom, the swap routine finishes without changing the currentAmount (it remains zero). Because buy_amt_min is also zero, the final require check (currentAmount >= buy_amt_min) passes, and the function returns 0 as the amount of ETH received. From the user’s perspective the transaction appears to have succeeded – the contract emitted no error – but the user receives no ETH and the transferred tokens remain locked in the contract, effectively disappearing from the user’s balance. The issue occurs only when two conditions are met simultaneously: (1) the route array contains exactly one token (the input token itself) and (2) the caller specifies a zero‑slippage or zero‑minimum‑output value. It was discovered during a security audit that examined the swap implementation and identified that the route length was never validated and that a zero buy_amt_min could be used to bypass output checks. The bug is subtle because the transaction does not revert; it simply performs a no‑op swap, making it easy to miss during testing unless the specific edge case is exercised. The flaw belongs to the class of input‑validation errors where insufficient parameter checks allow a function to execute without performing its intended logic, leading to loss of funds. To remediate, the contract should enforce a minimum route length greater than one (e.g., require(route.length > 1)) and reject zero or unreasonably low buy_amt_min values unless explicitly allowed, thereby ensuring that a swap always involves at least one hop and that the caller cannot accept a zero output. This correction restores the intended business logic that a swap must convert the input token into a non‑zero amount of the target token, preserving user funds and aligning contract behavior with user expectations.

## Proof of Concept
1. User calls swapForETH function with below params:

    pay_amt=500
    buy_amt_min=0
    route[0]=WETH
    expectedMarketFeeBPS=1

2. User will transfer 500+fees amount to the contract

```solidity
    require(
        ERC20(route[0]).transferFrom(
            msg.sender,
            address(this),
            pay_amt.add(pay_amt.mul(expectedMarketFeeBPS).div(10000))
        ),
        "initial ERC20 transfer failed"
    );
```

3. Now _swap function is called. This function will do nothing and loop will not run due to condition failure

```solidity
    for (uint256 i = 0; i < route.length - 1; i++)
```

// here since route.length - 1 is 1-1=0 so loop will not run as i=0 and 0<0 is false

4. Since currentAmount will be 0 and buy_amt_min is also 0 so require(currentAmount >= buy_amt_min, “didnt clear buy_amt_min”); will pass and 0 will be returned back
5. Swap is complete and user will not receive anything

## Recommendation
Add below check
    
```solidity
    require(route.length > 1, "Invalid route param");
```

Medium risk because it’s user error.

I think the problem is created by the warden by specifying `buy_amt_min=0`. If a slippage of 0 is specified then you basically anticipate that you may receive nothing. While enforcing min route length is a good suggestion, I do not think it should be that severe.

2 user errors have to be made for this to happen:

  * User specifies only 1 token in the route: WETH
  * Zero slippage: `buy_amt_min = 0`

Hence, because of these prerequisites, I will downgrade the issue to medium severity.
