### Title
Missing `address(0)` Validation for `owner` in `addLiquidity` Permanently Locks LP Tokens - (File: metric-core/contracts/MetricOmmPool.sol)

### Summary
`MetricOmmPool.addLiquidity` accepts `owner = address(0)` without reverting. Because `removeLiquidity` enforces `msg.sender == owner`, a position minted under the zero address can never be burned. Any tokens deposited into such a position are permanently locked inside the pool.

### Finding Description
`MetricOmmPool.addLiquidity` takes an arbitrary `owner` address and mints bin shares keyed by `keccak256(abi.encode(owner, salt, bin))`. No check is performed to ensure `owner != address(0)`. [1](#0-0) 

When `owner = address(0)` is supplied:
1. `LiquidityLib.addLiquidity` computes the position key with `address(0)`, increments `binTotalShares` and `positionBinShares[key]`, and updates `binTotals`.
2. The modify-liquidity callback fires and pulls real tokens from the caller into the pool.
3. The pool's accounting is internally consistent — the tokens are held and the shares exist — but the shares are permanently stranded. [2](#0-1) 

`removeLiquidity` enforces `msg.sender == owner`: [3](#0-2) 

Because no EOA or contract can produce a transaction with `msg.sender == address(0)`, the shares minted under the zero-address key can never be burned and the underlying tokens can never be recovered.

The periphery helper `MetricOmmPoolLiquidityAdder._validateOwner` does guard against this: [4](#0-3) 

But this guard exists only in the periphery. The core pool is a public contract and any caller can interact with it directly, bypassing the periphery entirely.

### Impact Explanation
Tokens deposited into a position owned by `address(0)` are permanently locked inside the pool. The pool's `binTotals` correctly account for them (they are not "lost" from the pool's balance sheet), but no address can ever call `removeLiquidity` to reclaim them. The depositor suffers a total, irrecoverable loss of their principal.

### Likelihood Explanation
`MetricOmmPool.addLiquidity` is a public external function callable by any address. A caller who interacts with the pool directly (not through `MetricOmmPoolLiquidityAdder`) and passes `address(0)` as `owner` — whether by mistake, through a buggy integration, or through a malicious wrapper — will permanently lose their deposited tokens. The trigger requires no special privilege and no unusual pool state.

### Recommendation
Add a zero-address guard at the top of `addLiquidity` in `MetricOmmPool.sol`, mirroring the check already present in the periphery:

```solidity
function addLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (uint256 amount0Added, uint256 amount1Added) {
+   if (owner == address(0)) revert InvalidOwner();
    if (deltas.binIdxs.length == 0) return (0, 0);
    ...
}
```

### Proof of Concept

```solidity
// Attacker calls the pool directly, bypassing MetricOmmPoolLiquidityAdder
pool.addLiquidity(
    address(0),   // owner = zero address
    0,            // salt
    deltas,       // e.g. 10_000 shares in bin 4
    callbackData, // pays tokens from attacker's balance
    ""
);

// Shares now exist under keccak256(abi.encode(address(0), 0, 4))
// Tokens are inside the pool and accounted for in binTotals
// No address can ever call removeLiquidity(address(0), ...) because
// msg.sender == address(0) is impossible
// => tokens are permanently locked
``` [5](#0-4)

### Citations

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

**File:** metric-core/contracts/MetricOmmPool.sol (L204-210)
```text
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    if (msg.sender != owner) revert NotPositionOwner();
    _beforeRemoveLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Removed, amount1Removed) = LiquidityLib.removeLiquidity(
      _liquidityContext(), owner, salt, deltas, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L121-131)
```text
          positionBinShares[posKey] = newUserShares;

          binBalanceDeltas[i] = BinBalanceDelta({
            // Safe: per-bin deltas are bounded by uint104 bin balances.
            // forge-lint: disable-next-line(unsafe-typecast)
            delta0Scaled: int256(amount0Scaled),
            // casting to int256 is safe because amount1Scaled is bounded by uint104 bin balances.
            // forge-lint: disable-next-line(unsafe-typecast)
            delta1Scaled: int256(amount1Scaled)
          });
        }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L242-247)
```text
      if (amount0Removed > 0) {
        IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
      }
      if (amount1Removed > 0) {
        IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
      }
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L247-249)
```text
  function _validateOwner(address owner) internal pure {
    if (owner == address(0)) revert InvalidPositionOwner();
  }
```
