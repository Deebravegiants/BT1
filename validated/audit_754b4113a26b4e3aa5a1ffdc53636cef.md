Audit Report

## Title
Unrestricted `sweepToken` and `unwrapWETH9` Allow Any Caller to Drain Router Token Balances — (File: metric-periphery/contracts/base/PeripheryPayments.sol)

## Summary
`PeripheryPayments.sweepToken` and `PeripheryPayments.unwrapWETH9` are `public payable` with no `msg.sender` check and a fully caller-controlled `recipient` parameter. Any address can invoke either function at any time and redirect the router's entire token or WETH balance to an arbitrary address. Both `MetricOmmSimpleRouter` and `MetricOmmPoolLiquidityAdder` inherit these helpers without restriction, making both contracts affected.

## Finding Description
`PeripheryPayments.unwrapWETH9` (L37–45) and `sweepToken` (L48–55) perform no caller validation:

```solidity
function unwrapWETH9(uint256 amountMinimum, address recipient) public payable override {
    uint256 balanceWETH = IERC20(WETH).balanceOf(address(this));
    if (balanceWETH < amountMinimum) revert InsufficientWETH(amountMinimum, balanceWETH);
    if (balanceWETH > 0) {
        IWETH9(WETH).withdraw(balanceWETH);
        _transferETH(recipient, balanceWETH);
    }
}

function sweepToken(address token, uint256 amountMinimum, address recipient) public payable override {
    uint256 balanceToken = IERC20(token).balanceOf(address(this));
    if (balanceToken < amountMinimum) revert InsufficientToken(token, amountMinimum, balanceToken);
    if (balanceToken > 0) {
        IERC20(token).safeTransfer(recipient, balanceToken);
    }
}
```

The only guard is the `amountMinimum` floor, which an attacker bypasses by passing `0`. The `recipient` is entirely attacker-supplied.

The documented WETH-unwrap pattern — confirmed by `test_multicall_tokenForWeth_thenUnwrapEth` — routes swap output to `address(router)` via `exactInputSingle(..., recipient: address(router))` and then calls `unwrapWETH9` to forward ETH. The test batches both calls inside a single `multicall` (which uses `delegatecall`), making it atomic. However, nothing in the interface NatSpec (`IPeripheryPayments.sol` L7–16) warns callers that these functions must be batched; a user who issues the two calls as separate transactions leaves WETH stranded on the router between blocks. An attacker watching the mempool can front-run the `unwrapWETH9` call with their own call supplying `recipient = attacker`, draining the full balance. The same race applies to any ERC-20 via `sweepToken`.

## Impact Explanation
Direct loss of user principal. A user who routes swap output to the router and calls `unwrapWETH9` or `sweepToken` in a separate transaction loses the entire stranded balance to the attacker. There is no recovery path: the transfer is irreversible and the router holds no record of the original depositor. This is a Critical/High direct loss of user funds, satisfying the allowed impact gate.

## Likelihood Explanation
The WETH-unwrap pattern is explicitly tested and is the only way to receive native ETH from a token-for-WETH swap. Users unfamiliar with `multicall` batching, or using wallets/scripts that issue sequential transactions, will strand WETH on the router. An attacker needs only to monitor the mempool for transactions that set `recipient: address(router)` and immediately call `unwrapWETH9(0, attacker)` or `sweepToken(token, 0, attacker)`. No privilege, deposit, or special setup is required beyond gas.

## Recommendation
Restrict both functions so they can only be invoked from within a `multicall` context. Because `multicall` uses `delegatecall`, `msg.sender` inside a delegated call is the original external caller, not `address(this)`. A direct (non-delegated) call has `msg.sender != address(this)`. Adding `require(msg.sender == address(this))` to both functions would block standalone calls while preserving the `multicall`-batched flow. Alternatively, track a per-caller depositor mapping so only the address that routed output to the router can sweep it. At minimum, add prominent NatSpec on both functions and on the interface stating that they must always be batched inside `multicall`.

## Proof of Concept
1. Alice calls `exactInputSingle` with `recipient: address(router)` and `tokenOut: WETH` as a standalone transaction. The transaction confirms; the router now holds `X` WETH.
2. Bob (attacker) observes Alice's confirmed transaction and calls `router.unwrapWETH9(0, bob)` before Alice's follow-up call.
3. `unwrapWETH9` reads `balanceWETH = X`, passes the `amountMinimum = 0` check, withdraws all WETH, and sends `X` ETH to Bob.
4. Alice's subsequent `unwrapWETH9(X, alice)` reverts with `InsufficientWETH(X, 0)`.
5. Alice loses `X` WETH; Bob gains `X` ETH at zero cost beyond gas.

The same attack applies to any ERC-20 via `sweepToken(token, 0, attacker)`.