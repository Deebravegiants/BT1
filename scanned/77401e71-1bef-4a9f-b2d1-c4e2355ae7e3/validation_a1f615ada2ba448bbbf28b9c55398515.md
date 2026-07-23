### Title
`addLiquidity` Missing `whenNotPaused` Guard Allows Deposits Into a Paused Pool — (`metric-core/contracts/MetricOmmPool.sol`)

---

### Summary

`MetricOmmPool.swap` is protected by `whenNotPaused`, but `MetricOmmPool.addLiquidity` is not. Any user can deposit real token balances into a pool that has been administratively or protocol-paused, directly analogous to the Futureswap M02 pattern of operating on a "closed" entity without a liveness check.

---

### Finding Description

`MetricOmmPool` exposes a `pauseLevel` state variable (0 = active, 1 = admin-paused, 2 = protocol-paused). The `_checkNotPaused` guard is applied only to `swap`:

```solidity
// swap — correctly guarded
function swap(...) external whenNotPaused nonReentrant(PoolActions.SWAP) ...
```

`addLiquidity` carries no such guard:

```solidity
// addLiquidity — no whenNotPaused
function addLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (uint256 amount0Added, uint256 amount1Added) {
``` [1](#0-0) [2](#0-1) [3](#0-2) 

The pool is paused precisely when the oracle is stale, manipulated, or the price is otherwise unsafe. Blocking swaps prevents arbitrage exploitation of a bad price, but allowing `addLiquidity` during that window lets new LPs deposit real token balances at the moment the pool's pricing is known to be unreliable.

---

### Impact Explanation

When the pool is unpaused after a price-disruption event, the resumed oracle price may differ materially from the price at which the LP deposited. Arbitrageurs can immediately execute swaps against the pool at the stale/corrected price, draining the newly deposited tokens. The LP suffers a direct loss of principal with no recourse. `binTotals.scaledToken0` / `scaledToken1` are updated by `LiquidityLib.addLiquidity` during the paused state, so the accounting is real and the tokens are genuinely at risk. [4](#0-3) 

---

### Likelihood Explanation

- Pause events are a normal operational action (admin or protocol can trigger them).
- Any unprivileged user can call `addLiquidity` at any time; no special role is required.
- The window between a pause and the resolution of the underlying oracle issue is the attack surface; a user who is unaware of the pause (or a bot that does not check `pauseLevel`) will deposit into the unsafe pool.

---

### Recommendation

Apply `whenNotPaused` to `addLiquidity`, mirroring the protection already on `swap`:

```solidity
function addLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
) external whenNotPaused nonReentrant(PoolActions.ADD_LIQUIDITY) ...
```

`removeLiquidity` should intentionally remain unguarded so existing LPs can always exit. [5](#0-4) 

---

### Proof of Concept

1. Pool is deployed with a mutable `priceProvider`.
2. Admin calls `factory.setPause(pool, 1)` — pool is paused because the oracle is reporting a stale/manipulated price. `swap` now reverts.
3. Alice calls `pool.addLiquidity(...)` depositing 10,000 USDC worth of token0. The call succeeds; `binTotals.scaledToken0` increases; Alice's position shares are minted.
4. Admin resolves the oracle issue and calls `factory.setPause(pool, 0)` — pool is unpaused. The oracle now reports the correct (lower) price for token0.
5. Bob immediately calls `pool.swap(...)` buying token0 at the now-correct lower price, draining Alice's deposited token0 and paying less token1 than Alice's deposit was worth.
6. Alice calls `removeLiquidity` and receives far less than she deposited — direct loss of principal. [6](#0-5) [1](#0-0)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L81-82)
```text
  BinTotals internal binTotals;

```

**File:** metric-core/contracts/MetricOmmPool.sol (L182-196)
```text
  function addLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
  ) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (uint256 amount0Added, uint256 amount1Added) {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    _beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Added, amount1Added) = LiquidityLib.addLiquidity(
      _liquidityContext(), owner, salt, deltas, callbackData, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterAddLiquidity(msg.sender, owner, salt, deltas, amount0Added, amount1Added, extensionData);
  }
```

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

**File:** metric-core/contracts/MetricOmmPool.sol (L217-224)
```text
  function swap(
    address recipient,
    bool zeroForOne,
    int128 amountSpecified,
    uint128 priceLimitX64,
    bytes calldata callbackData,
    bytes calldata extensionData
  ) external whenNotPaused nonReentrant(PoolActions.SWAP) returns (int128, int128) {
```

**File:** metric-core/contracts/MetricOmmPool.sol (L454-461)
```text
  /// @inheritdoc IMetricOmmPoolFactoryActions
  function setPause(uint8 newLevel) external onlyFactory {
    if (newLevel > 2) revert InvalidPauseLevel();
    if (newLevel == pauseLevel) return;
    uint8 prev = pauseLevel;
    pauseLevel = newLevel;
    emit PauseLevelUpdated(prev, newLevel);
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L643-645)
```text
  function _checkNotPaused() internal view {
    if (pauseLevel != 0) revert PoolPaused();
  }
```
