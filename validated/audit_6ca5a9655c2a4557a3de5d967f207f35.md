Audit Report

## Title
`addLiquidity` Accepts `address(0)` as `owner`, Permanently Locking Deposited Tokens — (`metric-core/contracts/MetricOmmPool.sol`)

## Summary

`MetricOmmPool.addLiquidity` accepts a caller-supplied `owner` address with no zero-address validation. Because `removeLiquidity` enforces `msg.sender == owner`, any liquidity minted under `address(0)` is permanently irrecoverable. The deposited tokens are locked inside the pool with no recovery path.

## Finding Description

`MetricOmmPool.addLiquidity` (L182–196) accepts `owner` as an external parameter and passes it directly to `LiquidityLib.addLiquidity` without any zero-address check:

```solidity
// metric-core/contracts/MetricOmmPool.sol L182-196
function addLiquidity(
    address owner,   // ← no zero-address check
    ...
) external nonReentrant(PoolActions.ADD_LIQUIDITY) ...
```

Inside `LiquidityLib.addLiquidity`, shares are minted to the position key `keccak256(abi.encode(owner, salt, bin))` (L72) and `binTotalShares`/`positionBinShares` are updated (L120–121). The callback then pulls real tokens from `msg.sender` into the pool (L147–154).

`removeLiquidity` enforces `msg.sender == owner` (L206) before burning shares and transferring tokens back to `owner` (L242–247 of `LiquidityLib.sol`). If `owner == address(0)`:

1. Shares are minted to `keccak256(abi.encode(address(0), salt, bin))`.
2. Real tokens are pulled from the payer into the pool.
3. `removeLiquidity` requires `msg.sender == address(0)` — impossible for any EOA or contract.
4. Even if somehow reached, tokens would be sent to `address(0)` (burned).

The only guard against this exists in the periphery `MetricOmmPoolLiquidityAdder._validateOwner` (L247–249), which is absent from the core pool. Any caller that bypasses the periphery and calls `pool.addLiquidity(address(0), ...)` directly will permanently lock their deposited tokens.

## Impact Explanation

Tokens deposited via `addLiquidity(address(0), ...)` are permanently locked inside the pool. They are accounted in `binTotals.scaledToken0`/`scaledToken1` as LP-owned liquidity, so they are not accessible as spread fees or notional fees either. The payer loses their full deposit with no recovery path. This is a direct, permanent loss of user principal meeting Critical/High severity thresholds.

## Likelihood Explanation

`addLiquidity` is a public external function explicitly designed for the operator pattern (`msg.sender` pays, `owner` holds the position), inviting direct integration by third-party contracts and routers. Any integrator that passes `address(0)` as `owner` — by mistake, by a bug in their own code, or by a missing validation — will permanently lose the deposited tokens. The periphery validates this, but the core pool does not, creating a gap that is invisible to integrators who read only the pool interface.

## Recommendation

Add a zero-address check for `owner` in `MetricOmmPool.addLiquidity` at the pool level, mirroring the guard already present in the periphery:

```solidity
function addLiquidity(
    address owner,
    ...
) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (...) {
+   if (owner == address(0)) revert InvalidOwner();
    if (deltas.binIdxs.length == 0) return (0, 0);
    ...
```

Alternatively, enforce it inside `LiquidityLib.addLiquidity` so the invariant is upheld regardless of the call path.

## Proof of Concept

```solidity
// Attacker or mistaken integrator calls pool directly, bypassing periphery
pool.addLiquidity(
    address(0),   // owner = zero address
    0,            // salt
    deltas,       // valid bin deltas
    callbackData, // pays tokens in callback
    ""
);
// Tokens are now in the pool, accounted under posKey = keccak256(abi.encode(address(0), 0, bin))
// removeLiquidity(address(0), ...) requires msg.sender == address(0) → impossible
// Tokens are permanently locked
```

The position key `keccak256(abi.encode(address(0), salt, bin))` holds shares that can never be burned. The `binTotals.scaledToken0`/`scaledToken1` counters include these tokens, so they are not recoverable as fee surplus either.