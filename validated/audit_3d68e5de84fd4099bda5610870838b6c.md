Audit Report

## Title
Unauthenticated `addLiquidity` Enables Front-Running DoS on LP Full Withdrawal via `MinimalLiquidity` Revert — (`metric-core/contracts/libraries/LiquidityLib.sol`)

## Summary

`MetricOmmPool.addLiquidity` accepts an arbitrary `owner` address with no `msg.sender == owner` guard, allowing any caller to inject shares into any position. Combined with the `MinimalLiquidity` dust guard in `LiquidityLib.removeLiquidity`, an attacker can front-run a victim LP's full-withdrawal transaction with a calibrated dust deposit, causing the victim's withdrawal to revert because the residual share count falls in the forbidden range `(0, minimalMintableLiquidity)`. The attacker can repeat this on every retry, creating a persistent DoS on the victim's withdrawal path while their funds remain locked.

## Finding Description

`removeLiquidity` enforces `msg.sender == owner` before burning shares: [1](#0-0) 

`addLiquidity` has no equivalent guard — any caller may credit shares to any `owner`: [2](#0-1) 

Inside `LiquidityLib.addLiquidity`, shares are written to the position key `(owner, salt, bin)` derived from the caller-supplied `owner`, not from `msg.sender`: [3](#0-2) 

Inside `LiquidityLib.removeLiquidity`, after subtracting the requested shares, the dust guard fires whenever the remainder is non-zero but below `minimalMintableLiquidity`: [4](#0-3) 

The optional `_beforeAddLiquidity` extension hook does not close this gap. The `DepositAllowlistExtension` checks the `owner` argument (the victim's address), not `msg.sender` (the attacker), so a victim who is a legitimate LP is already on any allowlist and the attacker's call passes through: [5](#0-4) 

Pools without any extension configured have no hook at all, leaving the path completely open.

## Impact Explanation

The victim LP's `removeLiquidity` transaction reverts with `MinimalLiquidity`. Their tokens remain locked in the pool. The attacker can repeat the front-run on every retry, sustaining the DoS indefinitely. This directly breaks the core liquidity-removal flow for targeted positions, matching the allowed impact gate criterion: *Broken core pool functionality causing loss of funds or unusable withdraw/swap/liquidity flows.* [4](#0-3) 

## Likelihood Explanation

- The victim's `(owner, salt, bin)` tuple is fully observable from their pending mempool transaction or prior on-chain history.
- No privileged role is required; any EOA or contract can call `addLiquidity` with a victim's `owner` and `salt`.
- The attack is most effective against LPs attempting a full exit (all shares in a bin), which is a common operation.
- The attacker must pay proportional tokens per front-run (economically costly to sustain), but does not prevent targeted griefing by a motivated actor. [2](#0-1) 

## Recommendation

Add an `msg.sender == owner` authorization check to `addLiquidity`, mirroring the guard already present in `removeLiquidity`:

```solidity
// MetricOmmPool.sol – addLiquidity
if (msg.sender != owner) revert NotPositionOwner();
```

If third-party deposits on behalf of an owner are an intentional design feature, introduce an explicit approval mapping (e.g., `approvedDepositors[owner][depositor]`) so that only addresses whitelisted by the owner can inject shares into their position. [6](#0-5) 

## Proof of Concept

```
State: victim holds 10 000 shares in bin 4, salt S.
       minimalMintableLiquidity = 1 000.

Step 1 – Victim submits:
  pool.removeLiquidity(victim, S, [{bin:4, shares:10_000}], "")

Step 2 – Attacker front-runs (same block, higher gas):
  pool.addLiquidity(victim, S, [{bin:4, shares:500}], callbackData, "")
  // Attacker pays tokens; victim's positionBinShares[(victim,S,4)] becomes 10 500.

Step 3 – Victim's tx executes:
  userShares      = 10 500
  sharesToRemove  = 10 000
  newUserShares   = 500          // > 0 and < 1 000
  → revert MinimalLiquidity(500, 1000)

Step 4 – Victim's funds remain locked.
         Attacker repeats Step 2 on every retry.
```

Foundry test plan: deploy a pool with `minimalMintableLiquidity = 1000`, have `victim` add 10 000 shares, then `vm.prank(attacker)` call `addLiquidity(victim, salt, [{bin, 500}], ...)`, then assert that `victim`'s subsequent `removeLiquidity` for 10 000 shares reverts with `MinimalLiquidity(500, 1000)`. [3](#0-2)

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

**File:** metric-core/contracts/MetricOmmPool.sol (L199-206)
```text
  function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    nonReentrant(PoolActions.REMOVE_LIQUIDITY)
    returns (uint256 amount0Removed, uint256 amount1Removed)
  {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    if (msg.sender != owner) revert NotPositionOwner();
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L72-79)
```text
          bytes32 posKey = _positionBinKey(owner, salt, int8(binIdx));
          uint256 binTotalSharesVal = binTotalShares[binIdx];
          uint256 userShares = positionBinShares[posKey];

          uint256 newUserShares = userShares + sharesToAdd;
          if (newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L199-202)
```text
          uint256 newUserShares = userShares - sharesToRemove;
          if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }
```

**File:** metric-periphery/contracts/extensions/DepositAllowlistExtension.sol (L32-42)
```text
  function beforeAddLiquidity(address, address owner, uint80, LiquidityDelta calldata, bytes calldata)
    external
    view
    override
    returns (bytes4)
  {
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][owner]) {
      revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
  }
```
