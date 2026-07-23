Audit Report

## Title
Smart-contract LP owner permanently locked out of `removeLiquidity` — (`metric-core/contracts/MetricOmmPool.sol`)

## Summary
`MetricOmmPool.removeLiquidity` enforces `msg.sender == owner` at line 206, while `addLiquidity` deliberately supports an operator pattern where `msg.sender` and `owner` are distinct. Any smart-contract `owner` that cannot itself dispatch `pool.removeLiquidity(address(this), ...)` has its LP principal permanently locked in the pool with no alternative withdrawal path.

## Finding Description
`removeLiquidity` hard-gates on `msg.sender == owner`:

```solidity
// MetricOmmPool.sol L206
if (msg.sender != owner) revert NotPositionOwner();
```

`addLiquidity` imposes no such restriction — `owner` is a freely chosen address while `msg.sender` pays via callback:

```solidity
// MetricOmmPool.sol L182-196
function addLiquidity(address owner, uint80 salt, ...) external ...
```

The periphery `MetricOmmPoolLiquidityAdder.addLiquidityExactShares` (L56-68) explicitly documents and exercises this operator pattern, passing `msg.sender` as payer while recording a distinct `owner` as position holder. The position key is `keccak256(abi.encode(owner, salt, bin))` (LiquidityLib.sol L256-258), so only `msg.sender == owner` can ever call `removeLiquidity` for that key. `LiquidityLib.removeLiquidity` already transfers proceeds to `owner` (L242-247), not to `msg.sender`, so the identity check provides no fund-redirection protection — it only blocks legitimate operator withdrawals. There is no operator approval mapping, no factory escape hatch, and no alternative withdrawal path.

## Impact Explanation
LP principal (token0 and token1) deposited under a smart-contract `owner` address is permanently irrecoverable if that contract cannot itself dispatch `removeLiquidity`. This is a direct, irreversible loss of user funds meeting the "broken core pool functionality causing loss of funds or unusable withdraw/liquidity flows" criterion. Severity: High.

## Likelihood Explanation
The operator pattern (`owner != msg.sender`) is a first-class, documented feature of both the core pool and the periphery adder. Any integrator using `addLiquidityExactShares(pool, contractAddress, ...)` or `addLiquidityWeighted(pool, contractAddress, ...)` where `contractAddress` lacks a `removeLiquidity` dispatch path triggers the lock. Vaults, multisigs, DAO treasuries, and yield aggregators are common and realistic `owner` values in this pattern.

## Recommendation
Remove the `msg.sender == owner` guard from `removeLiquidity`. Tokens are already sent to `owner` by `LiquidityLib.removeLiquidity`, so fund redirection is impossible regardless of who calls the function:

```solidity
// Remove this line:
if (msg.sender != owner) revert NotPositionOwner();
```

If stricter access control is desired, introduce an explicit operator approval mapping (`approvedOperators[owner][msg.sender]`) mirroring the pattern used in ERC-6909 or Uniswap v4, rather than the identity check.

## Proof of Concept
1. Deploy a `Vault` contract that calls `addLiquidityExactShares(pool, address(this), salt, deltas, ...)` — records `address(Vault)` as position `owner`.
2. `Vault` has no function that calls `pool.removeLiquidity(address(this), salt, deltas, ...)`.
3. Any EOA or contract calls `pool.removeLiquidity(address(Vault), salt, deltas, ...)` — reverts with `NotPositionOwner` because `msg.sender != address(Vault)`.
4. LP shares and underlying token0/token1 are permanently locked under the position key `keccak256(abi.encode(address(Vault), salt, bin))` with no recovery path.