# [M] User will loose funds

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-rubicon
Published: 2022-05-26
Source: https://github.com/code-423n4/2022-05-rubicon-findings/issues/87
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-rubicon/blob/main/contracts/RubiconRouter.sol#L519


# Vulnerability details

## Impact
User will loose funds if user accidentally pass route with only 1 value which is route[0]=X WETH while calling swapForETH or swapWithETH/swapEntireBalance/swap function

## Proof of Concept

1. User calls swapForETH function with below params:

```
pay_amt=500
buy_amt_min=0
route[0]=WETH
expectedMarketFeeBPS=1
```

2. User will transfer 500+fees amount to the contract 

```
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

```
for (uint256 i = 0; i < route.length - 1; i++)
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-05-rubicon-findings/issues/87_
