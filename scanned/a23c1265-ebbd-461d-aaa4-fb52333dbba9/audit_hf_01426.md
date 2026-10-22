# [H] RubiconRouter.swapEntireBalance

## Summary
Severity: High
Contest weight: 0.7961
Dataset id: 7385
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `swapEntireBalance()` function allows the user to pass a `buy_amt_min` value which is the minimum number of tokens they should receive from the swap. But, the function doesn’t pass the value to the underlying `swap()` function. Thus, the user’s min value will be ignored. Since that will result in unexpected outcomes where user funds might be lost, I rate this issue as HIGH.

## Proof of Concept
swapEntireBalance():

```solidity
function swapEntireBalance(
    uint256 buy_amt_min,
    address[] calldata route, // First address is what is being payed, Last address is what is being bought
    uint256 expectedMarketFeeBPS
) external returns (uint256) {
    //swaps msg.sender entire balance in the trade
    uint256 maxAmount = ERC20(route[0]).balanceOf(msg.sender);
    ERC20(route[0]).transferFrom(
        msg.sender,
        address(this),
        maxAmount // Account for expected fee
    );
    return
        _swap(
            maxAmount,
            maxAmount.sub(buy_amt_min.mul(expectedMarketFeeBPS).div(10000)), //account for fee
            route,
            expectedMarketFeeBPS,
            msg.sender
        );
}
```

The second parameter of the `_swap()` call should be the min out value. Instead `maxAmount.sub(buy_amt_min.mul(expectedMarketFeeBPS).div(10000))` is used.

Example:

```solidity
amount = 100
buy_amt_min = 99
expectedMarketFeeBPS = 500 // 5%

actual buy_amy_min = 100 - (99 * (500 / 10000)) = 95.05
```

So instead of using `99` the function uses `95.05` which could result in the user receiving fewer tokens than they expected.

## Recommendation
Pass `buy_amt_min` directly to `_swap()`.

[bghughes (Rubicon) marked as duplicate](https://github.com/code-423n4/2022-05-rubicon-findings/issues/52#issuecomment-1146688694):

Duplicate of [#104](https://github.com/code-423n4/2022-05-rubicon-findings/issues/104).

Not a duplicate. This has to do with applying a fee on `buy_amt_min` instead of passing the actual value directly. Lower slippage tolerance means potential loss of funds, hence the high severity.
