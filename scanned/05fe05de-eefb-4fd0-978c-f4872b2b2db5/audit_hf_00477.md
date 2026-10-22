# [M] Malicious users can createOrder

## Summary
Severity: Medium
Contest weight: 0.4596
Dataset id: 1918
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Malicious users can createOrder with 0 amount and can cause DOS / block users to fillOrder, cancelOrder
Malicious users will create huge numbers of orders with 0 amountIn.
Now if anyone wants to fillOrder or cancelOrder they can not do it because:
• Due to the block gas limit, there is a clear limitation in the amount of operation that can be handled in an Array.
• ArrayMutation::removeFromArray is called on fillOrder, cancelOrder functions.
• Now because the malicious users have created a huge amount of orders with 0 amount,
• When normal users go to fillOrder or cancelOrder they simply run out of gas while iterating a huge array of pendingOrderIds.
• This makes them and every one impossible to do any further action on fillOrder, cancelOrder

## Proof of Concept
```solidity
OracleLess::createOrder
function createOrder(
    IERC20 tokenIn,
    IERC20 tokenOut,
    uint256 amountIn,
    uint256 minAmountOut,
    address recipient,
    uint16 feeBips,
    bool permit,
    bytes calldata permitPayload
) external override returns (uint96 orderId) {
    //procure tokens
    procureTokens(tokenIn, amountIn, recipient, permit, permitPayload);
    //construct and store order
    orderId = MASTER.generateOrderId(recipient);
    orders[orderId] = Order({
        orderId: orderId,
        tokenIn: tokenIn,
        tokenOut: tokenOut,
        amountIn: amountIn,
        minAmountOut: minAmountOut,
        recipient: recipient,
        feeBips: feeBips
    });
    //store pending order
    pendingOrderIds.push(orderId);
    emit OrderCreated(orderId);
}
```

## Recommendation
We can add checks for the createOrder function something like this
require(amountIn > 0, "amount should be greater than 0")
Or can add code like the other Contracts
MASTER.checkMinOrderSize(tokenIn, amountIn);
