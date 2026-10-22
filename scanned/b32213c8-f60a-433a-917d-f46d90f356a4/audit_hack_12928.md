# [H] An attacker can take the profit expected by the `LimitOrders` contract

## Summary
Severity: High
Reporter: WhiteHatMage
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L137-L141
Type: audit-issue

## Details
# An attacker can take the profit expected by the `LimitOrders` contract

## Summary

`execute_limit_order()` expects to retain any extra profit from successful order executions as a fee if there is a surplus from the `amount_out` returned by Uniswap, compared to the minimum expected by the market creator in `amountOutMinimum`.

`execute_limit_order()` accepts setting a path. The first path must be the `token_in`, and the last path must be the `tokens_out`. But the middle path can be anything.

An attacker can set a middle path that returns `amount_out == amountOutMinimum`, capturing the extra profit himself.

## Vulnerability Detail

`execute_limit_order()` validates the first and last path, but not the middle one:

```python
    # ensure path is valid
    assert len(_path) in [2, 3], "[path] invlid path"
    assert len(_uni_pool_fees) == len(_path)-1, "[path] invalid fees"
    assert _path[0] == order.token_in, "[path] invalid token_in"
    assert _path[len(_path)-1] == order.token_out, "[path] invalid token_out"
```

Then extracts the paths to form the `path` that Uniswap expects:

```python
    path: Bytes[66] = empty(Bytes[66])
    if(len(_path) == 2):
        path = concat(convert(_path[0], bytes20), convert(_uni_pool_fees[0], bytes3), convert(_path[1], bytes20))
    elif(len(_path) == 3):
        path = concat(convert(_path[0], bytes20), convert(_uni_pool_fees[0], bytes3), convert(_path[1], bytes20), convert(_uni_pool_fees[1], bytes3), convert(_path[2], bytes20))
```

The swap is executed in Uniswap with the path, and `amount_out` is returned to indicate the tokens out amount:

```python
    uni_params: ExactInputParams = ExactInputParams({
        path: path,
        recipient: self,
        deadline: block.timestamp,
        amountIn: order.amount_in,
        amountOutMinimum: order.min_amount_out
    })
    amount_out: uint256 = UniswapV3SwapRouter(UNISWAP_ROUTER).exactInput(uni_params)
```

The contract expects that to take profit from `amount_out - min_amount_out`:

```python
    # transfer min_amount_out of token_out from self back to user
    # anything > min_amount_out stays in contract as profit
    self._safe_transfer(order.token_out, order.account, order.min_amount_out)
```

But as shown previously, the middle path does not have any validation. An attacker can create a path that makes `amount_out == min_amount_out` or a very similar value, while capturing the original profit in the middle path. This way the protocol will receive 0 profit or a minimal profit.

## Impact

An attacker can capture the profit that the `LimitOrders` contract expects to receive from order executions.

## Code Snippet

- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L137-L141
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L166-L170
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L173-L180
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L182-L184

## Tool used

Manual Review

## Recommendation

Apply a fee to the `amount_out` regardless of any expected profit, like it is done on the `Dca` contract.

Taken from the `DCA` contract:

```python
    # transfer amount_out - fee to user 
    amount_minus_fee: uint256 = amount_out * (FEE_BASE - self.fee) / FEE_BASE
    self._safe_transfer(order.token_out, order.account, amount_minus_fee)
```
