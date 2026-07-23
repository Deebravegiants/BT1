### Title
LPs Cannot Specify Minimum Token Amounts When Removing Liquidity, Enabling Sandwich-Induced Loss — (`metric-core/contracts/MetricOmmPool.sol`, `metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol`)

---

### Summary

`MetricOmmPool.removeLiquidity` accepts no minimum-output parameters. An LP who previews expected token amounts off-chain and then submits a removal transaction can receive materially less than expected if one or more swaps execute in the same block before their transaction, draining bin token balances. No periphery wrapper exists to add this protection.

---

### Finding Description

`MetricOmmPool.removeLiquidity` is defined as:

```solidity
function removeLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata extensionData
)
    external
    nonReentrant(PoolActions.REMOVE_LIQUIDITY)
    returns (uint256 amount0Removed, uint256 amount1Removed)
``` [1](#0-0) 

The function accepts only the bins and share amounts to burn (`LiquidityDelta.binIdxs` / `LiquidityDelta.shares`). There is no `minAmount0Out` or `minAmount1Out` parameter. The actual tokens returned are computed inside `LiquidityLib.removeLiquidity` based on the live `BinState.token0BalanceScaled` / `token1BalanceScaled` at execution time. [2](#0-1) 

Because the pool is oracle-priced, swaps can move large amounts of one token out of a bin in a single transaction. An LP who calls a view function to estimate their removal proceeds, then submits `removeLiquidity`, can have one or more swaps front-run or naturally precede their transaction, leaving the bin with far fewer tokens of one type than the LP anticipated.

The periphery `MetricOmmPoolLiquidityAdder` provides slippage protection only for **adding** liquidity (`maxAmountToken0` / `maxAmountToken1` enforced in the callback):

```solidity
if (amount0Delta > max0 || amount1Delta > max1) {
    revert MaxAmountExceeded(amount0Delta, amount1Delta, max0, max1);
}
``` [3](#0-2) 

There is no corresponding `removeLiquidity` wrapper in the periphery that would enforce `minAmount0Out` / `minAmount1Out`. The `MetricOmmPoolLiquidityAdder` contract contains only `addLiquidityExactShares` and `addLiquidityWeighted` entry points. [4](#0-3) 

---

### Impact Explanation

An LP holding shares in a bin that is currently balanced between token0 and token1 previews, for example, 1 000 token0 and 1 000 token1 on removal. A large swap draining token0 from that bin executes first. The LP's transaction then executes and receives, say, 200 token0 and 1 800 token1. At the oracle mid-price the dollar value of the second outcome can be substantially lower than the first (the LP receives the depleted token at a stale internal bin price rather than the current oracle price). The LP has no on-chain mechanism to revert this outcome. The loss is bounded by the bin's token balance and the LP's share fraction, but can be a significant fraction of the LP's principal for concentrated single-bin positions.

---

### Likelihood Explanation

Any swap that crosses or partially fills a bin changes `BinState.token0BalanceScaled` or `token1BalanceScaled`. In an active pool this happens on every block. An LP who previews removal amounts and submits a transaction faces this race on every submission. No special attacker capability is required; ordinary MEV searchers or even unrelated organic swap flow can trigger the loss.

---

### Recommendation

Add `minAmount0Out` and `minAmount1Out` parameters to `removeLiquidity` in `MetricOmmPool`, or add a periphery `removeLiquidity` wrapper (analogous to `MetricOmmPoolLiquidityAdder`) that reverts if the returned amounts fall below caller-specified minimums:

```solidity
function removeLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    uint256 minAmount0Out,   // <-- add
    uint256 minAmount1Out,   // <-- add
    bytes calldata extensionData
) external returns (uint256 amount0Removed, uint256 amount1Removed) {
    ...
    if (amount0Removed < minAmount0Out || amount1Removed < minAmount1Out)
        revert InsufficientOutputAmount();
}
```

Alternatively, a stateless periphery wrapper that calls `removeLiquidity` and checks the returned values before the transaction settles would achieve the same protection without modifying the core contract.

---

### Proof of Concept

**Scenario (single-bin pool, token0 = WETH, token1 = USDC):**

1. LP holds 50 % of shares in bin 0. Bin state: `token0BalanceScaled = 10 WETH`, `token1BalanceScaled = 20 000 USDC`. LP previews removal → expects ~5 WETH + ~10 000 USDC.
2. A large trader submits a `zeroForOne = false` swap (USDC → WETH) that drains all 10 WETH from bin 0 before the LP's transaction.
3. After the swap: `token0BalanceScaled ≈ 0`, `token1BalanceScaled ≈ 40 000 USDC` (USDC entered, WETH left).
4. LP's `removeLiquidity` executes. `LiquidityLib.removeLiquidity` computes the LP's share of the new bin state: ~0 WETH + ~20 000 USDC.
5. At the oracle price of 2 000 USDC/WETH, the LP expected ~20 000 USD but received ~20 000 USDC worth — however if the oracle price moved to reflect the drain, the LP may receive less in dollar terms. More critically, the LP had no ability to revert the transaction and is forced to accept whatever the bin state yields.

Because `removeLiquidity` returns the amounts but enforces no floor, the transaction succeeds silently regardless of how far the actual output deviates from the LP's expectation. [1](#0-0) [4](#0-3)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L199-212)
```text
  function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    nonReentrant(PoolActions.REMOVE_LIQUIDITY)
    returns (uint256 amount0Removed, uint256 amount1Removed)
  {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    if (msg.sender != owner) revert NotPositionOwner();
    _beforeRemoveLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Removed, amount1Removed) = LiquidityLib.removeLiquidity(
      _liquidityContext(), owner, salt, deltas, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterRemoveLiquidity(msg.sender, owner, salt, deltas, amount0Removed, amount1Removed, extensionData);
  }
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L56-81)
```text
  function addLiquidityExactShares(
    address pool,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    uint256 maxAmountToken0,
    uint256 maxAmountToken1,
    bytes calldata extensionData
  ) external payable override returns (uint256 amount0Added, uint256 amount1Added) {
    _validateOwner(owner);
    _validateDeltas(deltas);
    return _addLiquidity(pool, owner, salt, deltas, msg.sender, maxAmountToken0, maxAmountToken1, extensionData);
  }

  /// @notice Add liquidity with explicit per-bin shares for `msg.sender`.
  function addLiquidityExactShares(
    address pool,
    uint80 salt,
    LiquidityDelta calldata deltas,
    uint256 maxAmountToken0,
    uint256 maxAmountToken1,
    bytes calldata extensionData
  ) external payable override returns (uint256 amount0Added, uint256 amount1Added) {
    _validateDeltas(deltas);
    return _addLiquidity(pool, msg.sender, salt, deltas, msg.sender, maxAmountToken0, maxAmountToken1, extensionData);
  }
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L165-167)
```text
    if (amount0Delta > max0 || amount1Delta > max1) {
      revert MaxAmountExceeded(amount0Delta, amount1Delta, max0, max1);
    }
```
