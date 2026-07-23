### Title
Unrestricted `addLiquidity` Allows Front-Running to Permanently DoS LP Full Withdrawals via `MinimalLiquidity` Guard — (`metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

`addLiquidity` imposes no `msg.sender == owner` restriction, allowing any caller to deposit shares into an arbitrary LP's position. `removeLiquidity` contains a `MinimalLiquidity` guard that reverts if the remaining shares after a burn are `> 0` but `< MINIMAL_MINTABLE_LIQUIDITY`. An attacker can front-run a victim's full-withdrawal transaction by adding a dust-sized share increment to the victim's position, causing the victim's exact-share burn to leave a sub-minimal residual and revert indefinitely.

---

### Finding Description

**Root cause — asymmetric access control between `addLiquidity` and `removeLiquidity`:**

`removeLiquidity` enforces `msg.sender == owner`: [1](#0-0) 

`addLiquidity` has no such guard — any caller may supply any `owner` address: [2](#0-1) 

**The triggering guard in `removeLiquidity`:**

```solidity
uint256 newUserShares = userShares - sharesToRemove;
if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
    revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
}
``` [3](#0-2) 

**Why the attacker's `addLiquidity` call succeeds:** The `addLiquidity` guard only checks that `newUserShares = userShares + sharesToAdd >= MINIMAL_MINTABLE_LIQUIDITY`. Because the victim already holds a valid position (`userShares >= MINIMAL_MINTABLE_LIQUIDITY`), adding even 1 share satisfies this check regardless of how small `sharesToAdd` is: [4](#0-3) 

---

### Impact Explanation

The victim LP cannot execute a full withdrawal of their position. Their funds remain locked in the pool for as long as the attacker repeats the front-run. Because the attacker's cost per attack is a single dust-share deposit (1 wei of scaled token), the attack is economically viable to sustain indefinitely. This constitutes broken core pool functionality causing loss of access to LP principal — a direct match to the "unusable withdraw/liquidity flows" impact gate.

---

### Likelihood Explanation

- The victim's `owner`, `salt`, and `binIdx` are all emitted in `LiquidityAdded` / `LiquidityRemoved` events and are fully observable on-chain.
- The attacker only needs to monitor the mempool for `removeLiquidity` calls where `sharesToRemove == positionBinShares[posKey]` (a full exit).
- The cost per front-run is negligible: 1 share of scaled token plus gas.
- No privileged role is required; any EOA or contract can call `addLiquidity` with an arbitrary `owner`.

Likelihood: **Medium** (requires mempool visibility / front-running infrastructure, but is trivially cheap and repeatable).

---

### Recommendation

**Option A (minimal fix):** Mirror `removeLiquidity`'s access control in `addLiquidity` — require `msg.sender == owner` or an explicit approval mapping, so no third party can mutate another LP's position without consent.

**Option B (guard fix):** In `removeLiquidity`, treat a post-burn residual below `MINIMAL_MINTABLE_LIQUIDITY` as a full exit (set `newUserShares = 0`) rather than reverting, so the guard cannot be weaponised by an inflated share balance.

Option A is preferred because it also eliminates the broader griefing surface of forced liquidity injection into positions the owner did not authorise.

---

### Proof of Concept

```
Setup:
  MINIMAL_MINTABLE_LIQUIDITY = 1000 (pool immutable)
  Victim holds 50_000 shares in bin 4, salt 99

Step 1 — Victim submits (pending in mempool):
  removeLiquidity(owner=victim, salt=99, deltas={bin=4, shares=50_000})
  → newUserShares = 50_000 - 50_000 = 0  ✓ (would succeed)

Step 2 — Attacker front-runs:
  addLiquidity(owner=victim, salt=99, deltas={bin=4, shares=1})
  → newUserShares = 50_000 + 1 = 50_001 >= 1000  ✓ (add guard passes)
  → victim's positionBinShares[posKey] = 50_001

Step 3 — Victim's original tx executes:
  sharesToRemove = 50_000, userShares = 50_001
  newUserShares = 50_001 - 50_000 = 1
  1 > 0 && 1 < 1000  → revert MinimalLiquidity(1, 1000)

Step 4 — Attacker repeats Step 2 for every subsequent withdrawal attempt.
  Victim's funds are permanently locked.
```

The position key is deterministic (`keccak256(abi.encode(owner, salt, int8(binIdx)))`), so the attacker can target any known position with zero ambiguity. [5](#0-4)

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

**File:** metric-core/contracts/MetricOmmPool.sol (L206-206)
```text
    if (msg.sender != owner) revert NotPositionOwner();
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L76-79)
```text
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

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L256-259)
```text
  function _positionBinKey(address owner, uint80 salt, int8 bin) internal pure returns (bytes32 key) {
    // forge-lint: disable-next-line(asm-keccak256)
    return keccak256(abi.encode(owner, salt, bin));
  }
```
