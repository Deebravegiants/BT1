# [M] Spot dex should check the balance difference before and after the transfer

## Summary
Severity: Medium
Reporter: kutugu
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L201
Type: audit-issue

## Details
# Spot dex should check the balance difference before and after the transfer

## Summary

Spot dex supports transfer-on-fee tokens, should check the balance difference before and after the transfer.

## Vulnerability Detail

```solidity
# transfer token_in from user to self
    self._safe_transfer_from(order.token_in, order.account, self, order.amount_in)

    # approve UNISWAP_ROUTER to spend amount token_in
    ERC20(order.token_in).approve(UNISWAP_ROUTER, order.amount_in)

    path: Bytes[66] = empty(Bytes[66])
    if(len(_path) == 2):
        path = concat(convert(_path[0], bytes20), convert(_uni_pool_fees[0], bytes3), convert(_path[1], bytes20))
    elif(len(_path) == 3):
        path = concat(convert(_path[0], bytes20), convert(_uni_pool_fees[0], bytes3), convert(_path[1], bytes20), convert(_uni_pool_fees[1], bytes3), convert(_path[2], bytes20))
    

    uni_params: ExactInputParams = ExactInputParams({
        path: path,
        recipient: self,
        deadline: block.timestamp,
        amountIn: order.amount_in,
        amountOutMinimum: order.min_amount_out
    })
    amount_out: uint256 = UniswapV3SwapRouter(UNISWAP_ROUTER).exactInput(uni_params)
```

The transfer-on-fee tokens charge when the token is transferred, the protocol fails to receive the expected amount.
And the param passed in swap is `ExactInputParams`, which result in the agreement losing money (profit).

## Impact

The amount of the protocol received is smaller than expected, but spending is enough, resulting in a loss of funds.

## Code Snippet

- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L201
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L161

## Tool used

Manual Review

## Recommendation

check the balance difference before and after the transfer
