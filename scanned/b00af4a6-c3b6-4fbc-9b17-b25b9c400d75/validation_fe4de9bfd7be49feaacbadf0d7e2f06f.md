Based on my analysis of the codebase, I have found a valid analog.

---

### Title
Third-Party Deposit to Victim's Position Permanently Blocks `removeLiquidity` via `MinimalLiquidity` Dust Guard — (`metric-core/contracts/libraries/LiquidityLib.sol`, `metric-core/contracts/MetricOmmPool.sol`)

---

### Summary

`addLiquidity` accepts an arbitrary `owner` address (the operator pattern), meaning any caller can mint shares into any other user's position. The `removeLiquidity` path enforces a `MinimalLiquidity` dust guard that reverts if the remaining shares after a burn fall in the range `(0, minimalMintableLiquidity)`. An attacker can frontrun a victim's `removeLiquidity` call by depositing a tiny number of shares into the victim's position, causing the victim's exact-share removal to leave a sub-minimum dust remainder and revert. The attack can be repeated indefinitely, permanently freezing the victim's LP assets in the pool.

---

### Finding Description

`MetricOmmPool.addLiquidity` takes an explicit `owner` parameter that is fully decoupled from `msg.sender`: [1](#0-0) 

The interface documents this explicitly: *"msg.sender pays but need not equal owner (operator pattern)."* [2](#0-1) 

Inside `LiquidityLib.addLiquidity`, the only share-count guard is:

```solidity
uint256 newUserShares = userShares + sharesToAdd;
if (newUserShares < ctx.minimalMintableLiquidity) {
    revert IMetricOmmPoolActions.MinimalLiquidity(...);
}
``` [3](#0-2) 

Because `userShares` is the victim's **existing** balance, if the victim already holds `N >= minimalMintableLiquidity` shares, the attacker can add as few as **1 share** (`newUserShares = N + 1 >= minimalMintableLiquidity` — passes).

`removeLiquidity` enforces the complementary dust guard:

```solidity
uint256 newUserShares = userShares - sharesToRemove;
if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
    revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
}
``` [4](#0-3) 

`removeLiquidity` correctly enforces `msg.sender == owner`: [5](#0-4) 

But this only protects the **removal** path. The **addition** path has no such guard, creating the asymmetry the attack exploits.

**Attack sequence:**

1. Victim holds `N = 10 000` shares in bin `b`, salt `s` (`N >= minimalMintableLiquidity = 1 000`).
2. Victim submits `removeLiquidity(victim, s, [{bin: b, shares: 10 000}])`.
3. Attacker sees the tx in the mempool and frontruns with `addLiquidity(victim, s, [{bin: b, shares: 1}])`.
   - Check: `10 000 + 1 = 10 001 >= 1 000` → **passes**.
4. Victim's tx executes: `userShares = 10 001`, removes `10 000` → `newUserShares = 1`.
   - Check: `1 > 0 && 1 < 1 000` → **`MinimalLiquidity` revert**.
5. Victim's assets remain locked. Attacker repeats on every retry.

The cost per frontrun is approximately `binState.token0BalanceScaled / binTotalSharesVal` (1 share's worth), which is dust-level when the bin has many shares. The attacker's tokens are permanently credited to the victim's position (irrecoverable by the attacker since `removeLiquidity` requires `msg.sender == owner`), but the attack can be sustained cheaply.

The optional `DepositAllowlistExtension` does **not** mitigate this: it gates on the `owner` parameter, so if the victim is an allowed depositor, the attacker can still deposit to the victim's position using the victim's address as `owner`. [6](#0-5) 

---

### Impact Explanation

The victim's LP shares — and the underlying token0/token1 they represent — are permanently frozen in the pool. `removeLiquidity` is the only withdrawal path; there is no emergency exit or admin-forced removal. Every retry by the victim can be frontrun at negligible cost to the attacker. This constitutes a **direct, permanent loss of access to user principal** (LP assets), satisfying the Critical/High impact gate.

---

### Likelihood Explanation

- Requires mempool visibility (standard on all EVM chains without private mempools).
- Attacker must pay dust-level token amounts per frontrun; economically viable for any motivated adversary (competitor LP, short position holder, griever).
- No special permissions or privileged roles required — any EOA or contract can call `addLiquidity` with an arbitrary `owner`.
- Pools without `DepositAllowlistExtension` (the default, as confirmed by tests) are fully exposed.

**Likelihood: Medium** (requires active mempool monitoring and repeated frontruns, but is trivially scriptable).

---

### Recommendation

Enforce `msg.sender == owner` in `addLiquidity`, mirroring the guard already present in `removeLiquidity`:

```solidity
function addLiquidity(
    address owner,
    ...
) external nonReentrant(PoolActions.ADD_LIQUIDITY) ... {
    if (msg.sender != owner) revert NotPositionOwner(); // add this
    ...
}
```

If the operator pattern (third-party deposits) is intentional, add an explicit per-position approval mapping so only addresses approved by the owner can deposit into their position. Alternatively, remove the `MinimalLiquidity` revert in `removeLiquidity` for the case where the caller is removing their entire position (i.e., allow `newUserShares == 0` freely, which is already allowed, but also allow the caller to specify "remove all" atomically without knowing the exact current balance).

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

// Setup: pool with MINIMAL_MINTABLE_LIQUIDITY = 1000, bin 4 above current price.
// Victim has 10_000 shares in bin 4, salt = 0.

// Step 1: Victim submits (in mempool):
//   pool.removeLiquidity(victim, 0, LiquidityDelta({binIdxs:[4], shares:[10_000]}), "")

// Step 2: Attacker frontruns with:
contract Attacker {
    function frontrun(address pool, address victim, uint80 salt) external {
        // Add 1 share to victim's position — costs ~dust tokens
        int256[] memory bins = new int256[](1);
        bins[0] = 4;
        uint256[] memory shares = new uint256[](1);
        shares[0] = 1; // 1 share; passes MinimalLiquidity check since victim already has 10_000
        LiquidityDelta memory delta = LiquidityDelta({binIdxs: bins, shares: shares});
        // msg.sender (attacker) pays; owner = victim
        IMetricOmmPool(pool).addLiquidity(victim, salt, delta, callbackData, "");
    }
    // Attacker implements IMetricOmmModifyLiquidityCallback to pay the dust amount
}

// Step 3: Victim's tx executes:
//   userShares = 10_001, removes 10_000 → newUserShares = 1
//   1 > 0 && 1 < 1000 → MinimalLiquidity revert ✓

// Step 4: Victim retries with 10_001 shares → attacker frontruns again with 1 share → same revert.
// Victim's assets are permanently frozen.
```

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

**File:** metric-core/contracts/interfaces/IMetricOmmPool/IMetricOmmPoolActions.sol (L146-148)
```text
  /// @notice Mint shares across bins for `(owner, salt)`; pulls tokens via `IMetricOmmModifyLiquidityCallback` on `msg.sender`.
  /// @dev Callback receives native token amounts the pool expects; underpay reverts `InsufficientTokenBalance`. If `DEPOSIT_ALLOWLIST_PROVIDER` is set, `owner` must pass allowlist. `msg.sender` pays but need not equal `owner` (operator pattern).
  /// @param owner Position owner encoded in the pool’s position key.
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
